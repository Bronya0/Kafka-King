/*
 * Copyright 2025 Bronya0 <tangssst@163.com>.
 * Author Github: https://github.com/Bronya0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package service

import (
	"app/backend/common"
	"app/backend/types"
	"app/backend/utils/compress"
	"context"
	"crypto/tls"
	"crypto/x509"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net"
	"os"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/google/uuid"
	"github.com/twmb/franz-go/pkg/kerr"
	"github.com/twmb/franz-go/pkg/kmsg"
	"github.com/twmb/franz-go/pkg/sasl/aws"
	"github.com/twmb/franz-go/pkg/sasl/oauth"
	"github.com/twmb/franz-go/pkg/sr"
	"golang.org/x/crypto/ssh"

	"github.com/jcmturner/gokrb5/v8/client"
	krbConfig "github.com/jcmturner/gokrb5/v8/config"
	"github.com/jcmturner/gokrb5/v8/keytab"
	"github.com/twmb/franz-go/pkg/kadm"
	"github.com/twmb/franz-go/pkg/kgo"
	"github.com/twmb/franz-go/pkg/sasl/kerberos"
	"github.com/twmb/franz-go/pkg/sasl/plain"
	"github.com/twmb/franz-go/pkg/sasl/scram"
)

type TopicConfig struct {
	Name              string
	NumPartitions     int32
	ReplicationFactor int16
}

type Service struct {
	connectName      string
	bootstrapServers []string
	config           []kgo.Opt
	kac              *kadm.Client
	client           *kgo.Client
	oneShot          *oneShotCache // 单次消费的 client 缓存（与流式消费完全隔离）
	mutex            sync.Mutex
	topics           []any
	groups           []any
	sshTunnel        *sshTunnel // 新增：存储 SSH 隧道
	streams          map[string]*StreamInstance
	// Streaming
	appCtx context.Context // Wails 运行时 context，用于 EventsEmit

	// Schema Registry
	srMu     sync.Mutex
	srClient *sr.Client
	srCodecs map[int]string // schemaID -> schema 全文缓存
	srURL    string
}

// StreamState 兼容保留的结构体（旧版单流状态）
type StreamState struct {
	Running bool   `json:"running"`
	Topic   string `json:"topic"`
	Group   string `json:"group"`
}

// oneShotCache 缓存单次消费的 client，避免每次消费都重新加入消费组。
// key 包含全部会影响 client 配置的参数，任一变化即重建。
type oneShotCache struct {
	key    string
	client *kgo.Client
}

func (k *Service) ptr(s string) *string {
	return &s
}

// mapStr 从 map[string]any 中安全读取字符串（Wails 传参 key 可能缺失或类型不符）
func mapStr(m map[string]any, key string) string {
	if v, ok := m[key].(string); ok {
		return v
	}
	return ""
}

func NewKafkaService() *Service {
	return &Service{
		streams: map[string]*StreamInstance{},
	}
}

func (k *Service) Start(ctx context.Context) {
	k.appCtx = ctx
}

func (k *Service) Close(_ context.Context) bool {
	k.mutex.Lock()
	defer k.mutex.Unlock()

	if k.client != nil {
		k.client.Close()
	}
	if k.kac != nil {
		k.kac.Close()
	}
	if k.oneShot != nil && k.oneShot.client != nil {
		k.oneShot.client.Close()
		k.oneShot = nil
	}
	k.stopAllStreamsLocked()
	if k.sshTunnel != nil {
		_ = k.sshTunnel.client.Close()
		k.sshTunnel = nil
	}
	k.ClearSchemaRegistry()
	fmt.Println("连接已关闭")
	return false
}

// SSH 隧道配置
type sshTunnel struct {
	client   *ssh.Client
	dialFunc func(ctx context.Context, network, addr string) (net.Conn, error)
}

// setupSSHTunnel 建立 SSH 隧道
// 返回 SSH 客户端和一个 Dial 函数，该函数通过 SSH 隧道连接到任意目标地址。
// 配合 kgo.Dialer 使用，可使所有 Kafka broker 连接（包括元数据发现的新 broker）
// 都通过跳板机路由，解决仅第一个 bootstrap server 走隧道的问题。
func (k *Service) setupSSHTunnel(conn map[string]any) (*sshTunnel, error) {
	useSSH, ok := conn["use_ssh"].(string)
	if !ok || useSSH != "enable" {
		return nil, nil // SSH 未启用，正常返回 nil
	}

	sshHost, ok := conn["ssh_host"].(string)
	if !ok || sshHost == "" {
		return nil, errors.New("SSH host is required")
	}
	sshPortF, ok := conn["ssh_port"].(float64)
	if !ok {
		sshPortF = 22
	}
	sshPort := int(sshPortF)

	sshUser, ok := conn["ssh_user"].(string)
	if !ok || sshUser == "" {
		return nil, errors.New("SSH user is required")
	}

	// SSH 认证配置
	var authMethods []ssh.AuthMethod
	if sshPassword, ok := conn["ssh_password"].(string); ok && sshPassword != "" {
		authMethods = append(authMethods, ssh.Password(sshPassword))
	}
	if sshKeyFile, ok := conn["ssh_key_file"].(string); ok && sshKeyFile != "" {
		key, err := os.ReadFile(sshKeyFile)
		if err != nil {
			return nil, fmt.Errorf("failed to read SSH key file: %v", err)
		}
		signer, err := ssh.ParsePrivateKey(key)
		if err != nil {
			return nil, fmt.Errorf("failed to parse SSH key: %v", err)
		}
		authMethods = append(authMethods, ssh.PublicKeys(signer))
	}
	if len(authMethods) == 0 {
		return nil, errors.New("SSH authentication method is required (password or key)")
	}

	// SSH 客户端配置
	sshConfig := &ssh.ClientConfig{
		User:            sshUser,
		Auth:            authMethods,
		HostKeyCallback: ssh.InsecureIgnoreHostKey(), // WARNING: 仅用于开发环境
		Timeout:         10 * time.Second,
	}

	// 连接 SSH 服务器
	sshClient, err := ssh.Dial("tcp", fmt.Sprintf("%s:%d", sshHost, sshPort), sshConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to dial SSH server: %v", err)
	}

	// 通过 SSH 隧道 Dial 任意目标地址
	dialFunc := func(ctx context.Context, network, addr string) (net.Conn, error) {
		return sshClient.Dial(network, addr)
	}

	return &sshTunnel{
		client:   sshClient,
		dialFunc: dialFunc,
	}, nil
}

func (k *Service) SetConnect(connectName string, conn map[string]any, isTest bool) *types.ResultResp {
	k.mutex.Lock()
	defer k.mutex.Unlock()
	result := &types.ResultResp{}

	var config []kgo.Opt
	var sshTunnel *sshTunnel // 此处为本次连接尝试创建的隧道
	var err error

	connCopy := make(map[string]any)
	for k, v := range conn {
		connCopy[k] = v
	}

	// 尝试建立 SSH 隧道
	sshTunnel, err = k.setupSSHTunnel(connCopy)
	if err != nil {
		result.Err = fmt.Sprintf("SSH tunnel setup failed: %v", err)
		return result
	}
	if sshTunnel != nil {
		// 使用 kgo.Dialer 将所有 Kafka broker 连接路由到 SSH 隧道，
		// 包括元数据发现的其他 broker，不再需要替换 bootstrap_servers
		config = append(config, kgo.Dialer(sshTunnel.dialFunc))
	}

	// TLS配置
	if connCopy["tls"] == "enable" {
		tlsConfig := &tls.Config{
			InsecureSkipVerify: connCopy["skipTLSVerify"] == "true", // 开发环境可以设置为true
		}
		if certFile, keyFile := mapStr(connCopy, "tls_cert_file"), mapStr(connCopy, "tls_key_file"); certFile != "" && keyFile != "" {
			cert, err := tls.LoadX509KeyPair(certFile, keyFile)
			if err != nil {
				result.Err = fmt.Sprintf("loading x509 key pair failed: %v", err)
				return result
			}
			tlsConfig.Certificates = []tls.Certificate{cert}
		}
		if caFile := mapStr(connCopy, "tls_ca_file"); caFile != "" {
			caCert, err := os.ReadFile(caFile)
			if err != nil {
				result.Err = fmt.Sprintf("reading CA file failed: %v", err)
				return result
			}
			caCertPool := x509.NewCertPool()
			caCertPool.AppendCertsFromPEM(caCert)
			tlsConfig.RootCAs = caCertPool
		}
		config = append(config, kgo.DialTLSConfig(tlsConfig))
	}
	// SASL配置
	if connCopy["sasl"] == "enable" {
		user := mapStr(connCopy, "sasl_user")
		pwd := mapStr(connCopy, "sasl_pwd")
		mechanism := mapStr(connCopy, "sasl_mechanism")
		switch strings.ToUpper(mechanism) {
		case "PLAIN":
			config = append(config, kgo.SASL(plain.Auth{User: user, Pass: pwd}.AsMechanism()))
		case "SCRAM-SHA-256":
			config = append(config, kgo.SASL(scram.Auth{User: user, Pass: pwd}.AsSha256Mechanism()))
		case "SCRAM-SHA-512":
			config = append(config, kgo.SASL(scram.Auth{User: user, Pass: pwd}.AsSha512Mechanism()))
		case "OAUTHBEARER":
			// 静态令牌模式：token 填在 SASL 密码框中
			token := pwd
			if token == "" {
				token = mapStr(connCopy, "oauth_token")
			}
			if token == "" {
				result.Err = "OAUTHBEARER token is required (fill it in the SASL password field)"
				return result
			}
			config = append(config, kgo.SASL(oauth.Auth{Token: token}.AsMechanism()))
		case "AWS_MSK_IAM":
			// AccessKey 填 SASL 用户名，SecretKey 填 SASL 密码；MSK IAM 要求 TLS
			if user == "" || pwd == "" {
				result.Err = "AWS MSK IAM requires access key and secret key"
				return result
			}
			if connCopy["tls"] != "enable" {
				result.Err = "AWS MSK IAM requires TLS to be enabled"
				return result
			}
			config = append(config, kgo.SASL(aws.Auth{
				AccessKey:    user,
				SecretKey:    pwd,
				SessionToken: mapStr(connCopy, "sasl_session_token"),
			}.AsManagedStreamingIAMMechanism()))
		case "GSSAPI":
			kt, err := keytab.Load(mapStr(connCopy, "kerberos_user_keytab"))
			if err != nil {
				result.Err = err.Error()
				return result
			}
			cfg, err := krbConfig.Load(connCopy["kerberos_krb5_conf"].(string))
			if err != nil {
				result.Err = err.Error()
				return result
			}
			kerberosClient := client.NewWithKeytab(
				mapStr(connCopy, "Kerberos_user"),  // username (principal的第一部分)
				mapStr(connCopy, "Kerberos_realm"), // realm (Kerberos领域，大写的域名)
				kt,                                 // keytab对象
				cfg,                                // krb5配置对象
				client.DisablePAFXFAST(true),       // 禁用PA-FX-FAST，提高兼容性
			)
			// 创建GSSAPI认证
			config = append(config,
				kgo.SASL(kerberos.Auth{
					Client:           kerberosClient,
					Service:          mapStr(connCopy, "kerberos_service_name"),
					PersistAfterAuth: true,
				}.AsMechanism()))
		default:
			result.Err = fmt.Sprintf("unsupported SASL mechanism: %s", mechanism)
			return result
		}
	}
	bootstrapServersStr, ok := connCopy["bootstrap_servers"].(string)
	if !ok || bootstrapServersStr == "" {
		result.Err = "bootstrap_servers is required"
		return result
	}
	bootstrapServers := strings.Split(bootstrapServersStr, ",")

	config = append(
		config,
		kgo.SeedBrokers(bootstrapServers...),
		kgo.RecordPartitioner(newAutoPartitioner()),
	)

	cl, err := kgo.NewClient(config...)
	if err != nil {
		// FIX: 如果客户端创建失败，确保关闭此次调用创建的隧道
		if sshTunnel != nil {
			_ = sshTunnel.client.Close()
		}
		result.Err = "NewClient Error：" + err.Error()
		return result
	}

	admin := kadm.NewClient(cl)
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	topics, err := admin.ListTopics(ctx)
	if err != nil {
		// FIX: 如果连接测试失败，确保关闭客户端和隧道
		log.Println("连接集群失败", err)
		result.Err = "ListTopics Error：" + err.Error()
		admin.Close()
		cl.Close()
		if sshTunnel != nil {
			_ = sshTunnel.client.Close()
		}
		return result
	}

	if !isTest {
		// 正式切换：先关闭所有旧资源（当前持有 mutex）
		k.stopAllStreamsLocked()
		if k.client != nil {
			k.client.Close()
		}
		if k.kac != nil {
			k.kac.Close()
		}
		if k.oneShot != nil && k.oneShot.client != nil {
			k.oneShot.client.Close()
			k.oneShot = nil
		}
		if k.sshTunnel != nil {
			_ = k.sshTunnel.client.Close()
		}

		// 分配新资源
		k.connectName = connectName
		k.kac = admin
		k.client = cl
		k.config = config
		k.bootstrapServers = bootstrapServers
		k.sshTunnel = sshTunnel // 存储新的隧道，可能为 nil
		k.clearCache()
		k.topics = k.buildTopicsResp(topics)
	} else {
		// 测试连接：完成后关闭所有本次创建的资源
		admin.Close()
		cl.Close()
		if sshTunnel != nil {
			_ = sshTunnel.client.Close()
		}
	}

	return result
}

// TestClient 测试连接
func (k *Service) TestClient(connectName string, conn map[string]any) *types.ResultResp {
	return k.SetConnect(connectName, conn, true)
}

func (k *Service) clearCache() {
	k.topics = nil
	k.groups = nil
}

// GetBrokers 获取集群信息（含 Controller）
func (k *Service) GetBrokers() *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	brokers, err := k.kac.ListBrokers(ctx)
	if err != nil {
		result.Err = "ListBrokers Error：" + err.Error()
		return result
	}

	// 通过 Metadata 请求获取 controller（KRaft 模式下同样是 controller quorum leader）
	controllerID := int32(-1)
	if k.client != nil {
		mreq := kmsg.NewPtrMetadataRequest()
		if mres, err := k.client.Request(ctx, mreq); err == nil {
			if m, ok := mres.(*kmsg.MetadataResponse); ok {
				controllerID = m.ControllerID
			}
		}
	}

	brokersResp := make([]map[string]any, 0)
	for _, broker := range brokers {
		brokersResp = append(brokersResp, map[string]any{
			"node_id":       broker.NodeID,
			"host":          broker.Host,
			"port":          broker.Port,
			"rack":          broker.Rack,
			"is_controller": broker.NodeID == controllerID,
		})
	}
	clusterInfo := map[string]any{
		"brokers":       brokersResp,
		"controller_id": controllerID,
	}
	result.Result = clusterInfo
	return result
}

// GetBrokerConfig 获取Broker配置
func (k *Service) GetBrokerConfig(brokerID int32) *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx := context.Background()
	configs, err := k.kac.DescribeBrokerConfigs(ctx, brokerID)
	if err != nil {
		result.Err = fmt.Sprintf("DescribeBrokerConfigs Error：%s", err.Error())
		return result
	}
	if len(configs) == 0 {
		result.Err = "No configurations found for the given broker ID"
		return result
	}

	cfg := configs[0].Configs
	sort.Slice(cfg, func(i, j int) bool {
		return cfg[i].Key < cfg[j].Key
	})

	for _, config := range cfg {
		result.Results = append(result.Results, map[string]any{
			"Name":      config.Key,
			"Value":     config.Value,
			"Source":    config.Source.String(),
			"Sensitive": config.Sensitive,
		})
	}
	return result
}

func (k *Service) buildTopicsResp(topics kadm.TopicDetails) []any {
	// FIX: 对 map 进行排序以保证输出顺序稳定
	topicNames := make([]string, 0, len(topics))
	for name := range topics {
		topicNames = append(topicNames, name)
	}
	sort.Strings(topicNames)

	result := make([]any, 0, len(topicNames))
	for _, topicName := range topicNames {
		topicDetail := topics[topicName]
		partitionErrs := ""
		var partitions []any
		for _, partition := range topicDetail.Partitions {
			errMsg := ""
			if partition.Err != nil {
				errMsg = partition.Err.Error()
				partitionErrs += fmt.Sprintf("partition %d: %s\n", partition.Partition, errMsg)
			}
			partitions = append(partitions, map[string]any{
				"partition":       partition.Partition,
				"leader":          partition.Leader,
				"replicas":        partition.Replicas,
				"isr":             partition.ISR,
				"err":             errMsg,
				"LeaderEpoch":     partition.LeaderEpoch,
				"OfflineReplicas": partition.OfflineReplicas,
			})
		}
		if topicDetail.Err != nil {
			partitionErrs = topicDetail.Err.Error() + "\n" + partitionErrs
		}
		replicationFactor := 0
		if len(topicDetail.Partitions) > 0 {
			replicationFactor = len(topicDetail.Partitions[0].Replicas)
		}
		result = append(result, map[string]any{
			"ID":                 topicDetail.ID,
			"topic":              topicName,
			"partition_count":    len(topicDetail.Partitions),
			"replication_factor": replicationFactor,
			"IsInternal":         topicDetail.IsInternal,
			"Err":                partitionErrs,
			"partitions":         partitions,
		})
	}
	return result
}

// GetTopics 获取主题信息
func (k *Service) GetTopics(noCache bool) *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}

	if !noCache && len(k.topics) > 0 {
		result.Results = k.topics
		return result
	}

	ctx := context.Background()
	topics, err := k.kac.ListTopics(ctx)
	if err != nil {
		result.Err = fmt.Sprintf("ListTopics Error：%v", err.Error())
		return result
	}
	result.Results = k.buildTopicsResp(topics)

	k.topics = result.Results
	return result
}

// GetTopicConfig 获取主题配置
func (k *Service) GetTopicConfig(topic string) *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx := context.Background()

	res, err := k.kac.DescribeTopicConfigs(ctx, topic)
	if err != nil {
		result.Err = err.Error()
		return result
	}
	if len(res) == 0 {
		result.Err = "No configurations found for the given topic"
		return result
	}

	cfg := res[0].Configs
	sort.Slice(cfg, func(i, j int) bool {
		return cfg[i].Key < cfg[j].Key
	})

	for _, config := range cfg {
		result.Results = append(result.Results, map[string]any{
			"Name":      config.Key,
			"Value":     config.Value,
			"Source":    config.Source.String(), // 使用 .String() 方法
			"Synonyms":  config.Synonyms,
			"Sensitive": config.Sensitive,
		})
	}
	return result
}

func (k *Service) GetTopicOffsets(topics []string, groupID string) *types.ResultResp {
	result := &types.ResultResp{}

	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}

	ctx := context.Background()
	startOffsets, err := k.kac.ListStartOffsets(ctx, topics...)
	if err != nil {
		result.Err = "ListStartOffsets Error：" + err.Error()
		return result
	}

	endOffsets, err := k.kac.ListEndOffsets(ctx, topics...)
	if err != nil {
		result.Err = "ListEndOffsets Error：" + err.Error()
		return result
	}

	//读取offset。group 不存在等情况不阻塞 start/end 的展示
	committedOffsets, err := k.kac.FetchOffsetsForTopics(ctx, groupID, topics...)
	if err != nil {
		log.Printf("FetchOffsetsForTopics %s failed: %v", groupID, err)
		committedOffsets = kadm.OffsetResponses{}
	}

	// {"topicname":{"0":{"Topic":"1","Partition":0,"At":100,"LeaderEpoch":0,"Metadata":""},"1":。。。
	result.Result = map[string]any{
		"start_map":  k.ToMap(startOffsets.Offsets()),
		"end_map":    k.ToMap(endOffsets.Offsets()),
		"commit_map": k.ToMap(committedOffsets.Offsets()),
	}

	return result
}
func (k *Service) ToMap(mapStruct map[string]map[int32]kadm.Offset) map[string]map[int32]any {
	newMap := map[string]map[int32]any{}
	for k1, v := range mapStruct {
		if _, ok := newMap[k1]; !ok {
			newMap[k1] = make(map[int32]any)
		}
		for k2, v2 := range v {
			m := common.StructToMap(v2)
			newMap[k1][k2] = m
		}
	}
	return newMap
}

// GetGroups 获取消费组信息
func (k *Service) GetGroups() *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx := context.Background()
	groups, err := k.kac.ListGroups(ctx)
	if err != nil {
		result.Err = "ListGroups Error：" + err.Error()
		return result
	}

	sortedGroups := groups.Sorted()
	for _, group := range sortedGroups {
		result.Results = append(result.Results, map[string]any{
			"Group":        group.Group,
			"State":        group.State,
			"ProtocolType": group.ProtocolType,
			"Coordinator":  group.Coordinator,
		})
	}
	k.groups = result.Results
	return result
}

// GetGroupMembers 获取消费组下的成员信息
func (k *Service) GetGroupMembers(groupLst []string) *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx := context.Background()
	groups, err := k.kac.DescribeGroups(ctx, groupLst...)
	if err != nil {
		result.Err = "DescribeGroups Error：" + err.Error()
		return result
	}

	sortedGroups := groups.Sorted()
	for _, describedGroup := range sortedGroups {
		if describedGroup.Err != nil {
			// 单个 group 出错不阻塞其余 group 的展示
			log.Printf("describe group %s failed: %v", describedGroup.Group, describedGroup.Err)
			continue
		}
		membersLst := make([]any, 0)
		for _, member := range describedGroup.Members {
			subscribedTPs := make(map[string][]int32)
			// member.Assigned.AsConsumer(): 解析的是 "SyncGroup" 请求中的元数据。
			// 何时使用: 在 JoinGroup 阶段之后，消费者组的 Leader 会根据所有成员的订阅信息和分配策略，为每个成员分配具体的分区。然后，Leader 会通过 SyncGroup 请求将这个分配结果告诉 Broker，Broker 再将结果分发给各个成员。
			// 包含什么内容: 这部分元数据包含了最终的分区分配结果。也就是说，你能明确地知道这个消费者成员被分配到了哪些主题的哪些具体分区 (partitions)。
			// 关键点: 这是实际生效的分配方案。如果你想知道一个消费者当前正在处理哪些分区，应该查看这里的数据。
			if consumerMetadata, ok := member.Assigned.AsConsumer(); ok {
				tps := consumerMetadata.Topics
				for _, tp := range tps {
					subscribedTPs[tp.Topic] = tp.Partitions
				}
			}
			membersLst = append(membersLst, map[string]any{
				"MemberID":   member.MemberID,
				"InstanceID": member.InstanceID,
				"ClientID":   member.ClientID,
				"ClientHost": member.ClientHost,
				"TPs":        subscribedTPs, // TPs:map[topicName:[0]]]]
			})
		}
		result.Results = append(result.Results, map[string]any{
			"Group":        describedGroup.Group,
			"Coordinator":  describedGroup.Coordinator.Host,
			"State":        describedGroup.State,
			"ProtocolType": describedGroup.ProtocolType,
			"Protocol":     describedGroup.Protocol,
			"Members":      membersLst,
		})
	}
	return result
}

// CreateTopics 创建主题
func (k *Service) CreateTopics(topics []string, numPartitions, replicationFactor int, configs map[string]string) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}

	k.clearCache()

	// 转换为 map[string]*string
	pointerMap := make(map[string]*string)
	for key, value := range configs {
		pointerMap[key] = &value
	}

	ctx := context.Background()
	resp, err := k.kac.CreateTopics(ctx, int32(numPartitions), int16(replicationFactor), pointerMap, topics...)
	if err != nil {
		result.Err = "CreateTopics Error：" + err.Error()
		return result
	}
	err = resp.Error()
	if err != nil {
		result.Err = "CreateTopics Error：" + err.Error()
		return result
	}

	return result
}

// DeleteTopic 删除主题
func (k *Service) DeleteTopic(topics []string) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}

	k.clearCache()

	ctx := context.Background()
	for _, topic := range topics {
		resp, err := k.kac.DeleteTopic(ctx, topic)
		if err != nil {
			result.Err = "DeleteTopic Error：" + err.Error()
			return result
		}
		if resp.Err != nil {
			result.Err = "DeleteTopic Error：" + resp.Err.Error()
			return result
		}
	}
	return result
}

// DeleteGroup 删除Group
func (k *Service) DeleteGroup(group string) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}

	k.clearCache()

	ctx := context.Background()
	resp, err := k.kac.DeleteGroup(ctx, group)
	if err != nil {
		result.Err = "DeleteGroup Error：" + err.Error()
		return result
	}
	if resp.Err != nil {
		result.Err = "DeleteGroup Error：" + resp.Err.Error()
		return result
	}
	return result
}

// CreatePartitions 添加分区
func (k *Service) CreatePartitions(topics []string, count int) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}

	k.clearCache()

	ctx := context.Background()
	for _, topic := range topics {
		resp, err := k.kac.CreatePartitions(ctx, count, topic)
		if err != nil {
			result.Err = "CreatePartitions Error：" + err.Error()
			return result
		}
		err = resp.Error()
		if err != nil {
			result.Err = "CreatePartitions Error：" + err.Error()
			return result
		}
	}

	return result
}

// AlterTopicConfig 修改主题配置
func (k *Service) AlterTopicConfig(topic string, name, value string) *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ac := []kadm.AlterConfig{
		{
			Name:  name,
			Op:    kadm.SetConfig,
			Value: &value,
		},
	}

	ctx := context.Background()
	resp, err := k.kac.AlterTopicConfigs(ctx, ac, topic)
	if err != nil {
		result.Err = "AlterTopicConfigs Error：" + err.Error()
		return result
	}
	for _, v := range resp {
		if v.Err != nil {
			result.Err = "AlterTopicConfigs Error：" + v.Err.Error()
			return result
		}
	}
	return result
}

func (k *Service) AlterNodeConfig(nodeId int32, name, value string) *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ac := []kadm.AlterConfig{
		{
			Name:  name,
			Op:    kadm.SetConfig,
			Value: &value,
		},
	}

	ctx := context.Background()
	resp, err := k.kac.AlterBrokerConfigs(ctx, ac, nodeId)
	if err != nil {
		result.Err = "AlterBrokerConfigs Error：" + err.Error()
		return result
	}
	for _, v := range resp {
		if v.Err != nil {
			result.Err = "AlterBrokerConfigs Error：" + v.Err.Error()
			return result
		}
	}
	return result
}

// Produce 生产消息
func (k *Service) Produce(topic string, key, value string, partition, num int, headers []map[string]string, compressMethod string) *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.client == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	st := time.Now()
	headers2 := make([]kgo.RecordHeader, len(headers))
	for i := 0; i < len(headers); i++ {
		headers2[i] = kgo.RecordHeader{
			Key:   headers[i]["key"],
			Value: []byte(headers[i]["value"]),
		}
	}
	var data []byte
	var err error
	switch compressMethod {
	case "gzip":
		data, err = compress.Gzip([]byte(value))
	case "lz4":
		data, err = compress.Lz4([]byte(value))
	case "zstd":
		data, err = compress.Zstd([]byte(value))
	case "snappy":
		data, err = compress.Snappy([]byte(value))
	default:
		data = []byte(value)
	}
	if err != nil {
		result.Err = "Failed to compress data: " + err.Error()
		return result
	}
	var records []*kgo.Record
	for i := 0; i < num; i++ {
		// partition < 0 表示自动分配（按 key hash 或轮询）；>= 0 时 kgo 直接使用指定分区
		rec := &kgo.Record{
			Topic:     topic,
			Value:     data,
			Key:       []byte(key),
			Headers:   headers2,
			Partition: -1,
		}
		if partition >= 0 {
			rec.Partition = int32(partition)
		}
		records = append(records, rec)
	}
	res := k.client.ProduceSync(ctx, records...)
	if err := res.FirstErr(); err != nil {
		result.Err = "Produce Error：" + err.Error()
		return result
	}
	fmt.Printf("耗时：%.4f秒\n", time.Since(st).Seconds())
	return result
}

// ReproduceMessages 将消费到的消息回放到目标 topic。
// rows 来自 Consumer/流式消费的输出（Key、Value、Headers 等）；
// Headers 为 JSON 字符串形式 {"k":"v"}。
func (k *Service) ReproduceMessages(targetTopic string, rows []any) *types.ResultResp {
	result := &types.ResultResp{}
	if k.client == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	if targetTopic == "" {
		result.Err = "target topic is required"
		return result
	}
	if len(rows) == 0 {
		result.Err = "no messages to reproduce"
		return result
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	records := make([]*kgo.Record, 0, len(rows))
	for _, r := range rows {
		m, ok := r.(map[string]any)
		if !ok {
			continue
		}
		key, _ := m["Key"].(string)
		value, _ := m["Value"].(string)
		rec := &kgo.Record{
			Topic:     targetTopic,
			Key:       []byte(key),
			Value:     []byte(value),
			Partition: -1,
		}
		if hs, ok := m["Headers"].(string); ok && hs != "" {
			var hm map[string]string
			if err := json.Unmarshal([]byte(hs), &hm); err == nil {
				for hk, hv := range hm {
					rec.Headers = append(rec.Headers, kgo.RecordHeader{Key: hk, Value: []byte(hv)})
				}
			}
		}
		records = append(records, rec)
	}
	if len(records) == 0 {
		result.Err = "no valid messages to reproduce"
		return result
	}
	res := k.client.ProduceSync(ctx, records...)
	if err := res.FirstErr(); err != nil {
		result.Err = "Reproduce Error：" + err.Error()
		return result
	}
	result.Result = map[string]any{"count": len(records)}
	return result
}

// Consumer 消费消息（单次拉取）。
// startOffset > 0 时按该 offset 起始（对所有分区生效），优先级高于 isLatest/startTimestamp。
// 说明：client 缓存的 key 包含全部影响行为的参数；相同 key 复用 client 可以继续上次的进度，
// 与流式消费的 client 完全隔离，避免并发 PollRecords。
func (k *Service) Consumer(topic string, group string, num, timeout int, decompress string, isolationLevel string, isCommit, isLatest bool, startTimestamp int, startOffset int64, decode string) *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	st := time.Now()
	if topic == "" {
		result.Err = "topic is required"
		return result
	}
	if group == "" {
		group = "__kafka_king_auto_generate__"
	}

	// 缓存 key：任何影响 client 配置的参数都参与
	resetKey := fmt.Sprintf("%d|%d|%d", startTimestamp, bool2int(isLatest), startOffset)
	cacheKey := strings.Join([]string{group, topic, strings.ToLower(isolationLevel), resetKey}, "\x00")

	k.mutex.Lock()
	var _client *kgo.Client
	if k.oneShot == nil || k.oneShot.key != cacheKey {
		if k.oneShot != nil && k.oneShot.client != nil {
			k.oneShot.client.Close()
			k.oneShot = nil
		}
		_client, err := k.newConsumerClient(topic, group, isolationLevel, isLatest, startTimestamp, startOffset)
		if err != nil {
			k.mutex.Unlock()
			result.Err = "Consumer Error：" + err.Error()
			return result
		}
		k.oneShot = &oneShotCache{key: cacheKey, client: _client}
	}
	_client = k.oneShot.client
	k.mutex.Unlock()

	log.Println("开始poll...")
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)
	defer cancel()

	fetches := _client.PollRecords(ctx, num)

	if fetches.IsClientClosed() {
		k.mutex.Lock()
		if k.oneShot != nil && k.oneShot.client == _client {
			k.oneShot = nil
		}
		k.mutex.Unlock()
		result.Err = "Client Closed, Please Retry"
		return result
	}
	if errors.Is(ctx.Err(), context.DeadlineExceeded) {
		if len(fetches.Records()) == 0 {
			result.Err = "Consume Timeout, Maybe No Message"
			return result
		}
	}
	if errs := fetches.Errors(); len(errs) > 0 {
		errStrs := make([]string, 0, len(errs))
		for _, e := range errs {
			if errors.Is(e.Err, context.DeadlineExceeded) || errors.Is(e.Err, context.Canceled) {
				continue
			}
			errStrs = append(errStrs, e.Err.Error())
		}
		if len(errStrs) > 0 {
			result.Err = strings.Join(errStrs, "; ")
			return result
		}
	}
	log.Println("poll完成...", len(fetches.Records()))

	res := make([]any, 0)
	for i, v := range fetches.Records() {
		if v == nil {
			continue
		}
		row, err := k.buildMessageRow(v, decompress, decode)
		if err != nil {
			result.Err = "Failed to decode message: " + err.Error()
			return result
		}
		row["ID"] = i
		res = append(res, row)
	}
	result.Results = res

	fmt.Printf("耗时：%.4f秒\n", time.Since(st).Seconds())
	fmt.Println(topic, group, num)

	if group != "" && isCommit {
		log.Println("提交offset...")
		if err := _client.CommitUncommittedOffsets(context.Background()); err != nil {
			result.Err = "Failed to submit offsets: " + err.Error()
			return result
		}
	}
	return result
}

// newConsumerClient 创建一个用于消费（单次或流式）的 kgo client。
// 与主 client（k.client）分离，关闭互不影响。
func (k *Service) newConsumerClient(topic string, group string, isolationLevel string, isLatest bool, startTimestamp int, startOffset int64) (*kgo.Client, error) {
	if group == "__kafka_king_auto_generate__" {
		group = "__kafka_king__" + uuid.New().String()
	}
	conf := append(k.config,
		kgo.ConsumeTopics(topic),
		kgo.DisableAutoCommit(),
	)
	if strings.ToLower(isolationLevel) == "read_committed" {
		conf = append(conf, kgo.FetchIsolationLevel(kgo.ReadCommitted()))
	} else {
		conf = append(conf, kgo.FetchIsolationLevel(kgo.ReadUncommitted()))
	}
	conf = append(conf, kgo.ConsumerGroup(group))

	switch {
	case startOffset > 0:
		conf = append(conf, kgo.ConsumeResetOffset(kgo.NewOffset().At(startOffset)))
	case startTimestamp != 0:
		conf = append(conf, kgo.ConsumeResetOffset(kgo.NewOffset().AfterMilli(int64(startTimestamp))))
	case isLatest:
		conf = append(conf, kgo.ConsumeResetOffset(kgo.NewOffset().AtEnd()))
	default:
		conf = append(conf, kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()))
	}

	return kgo.NewClient(conf...)
}

func bool2int(b bool) int {
	if b {
		return 1
	}
	return 0
}

// getHeadersString 从RecordHeader切片获取json字符串
func getHeadersString(headers []kgo.RecordHeader) string {
	if len(headers) == 0 {
		return ""
	}

	headersMap := make(map[string]string)
	for _, h := range headers {
		headersMap[h.Key] = string(h.Value)
	}

	jsonBytes, err := json.Marshal(headersMap)
	if err != nil {
		//不影响主任务的执行，仅仅在对应的条目显示错误
		return err.Error()
	}

	return string(jsonBytes)
}

// GetAcls 获取 ACL 列表
// Kafka 在执行需要授权的操作（如描述 ACLs、创建主题、删除主题等）时，
// 会检查发出请求的客户端的身份（Principal），然后根据为该 Principal 配置的 ACL 规则来决定是否允许该操作。
// 如果你没有在 franz-go 客户端配置 SASL 或其他身份验证机制（如 TLS 客户端证书），broker 通常会将其视为 匿名用户 (Anonymous Principal)。
// 默认情况下，或者在安全配置得当的 Kafka 集群中，匿名用户通常没有执行敏感管理操作（包括描述所有 ACLs）的权限。描述所有 ACLs 需要对 Cluster 资源有 Describe 权限，这通常不会授予匿名用户。
func (k *Service) GetAcls() *types.ResultsResp {
	result := &types.ResultsResp{Results: make([]any, 0)}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	// 使用原始请求查询全部 ACL（所有过滤维度均为 Any）。
	// 不用 kadm 的 builder：它无法表达“任意 principal/host”的全通配查询，
	// 构造不出任何 describe 请求时会静默返回空列表。
	req := kmsg.NewPtrDescribeACLsRequest()
	req.ResourceType = kmsg.ACLResourceTypeAny
	req.ResourcePatternType = kmsg.ACLResourcePatternTypeAny
	req.Operation = kmsg.ACLOperationAny
	req.PermissionType = kmsg.ACLPermissionTypeAny
	resp, err := k.client.Request(ctx, req)
	if err != nil {
		result.Err = fmt.Sprintf("Failed to list ACLs: %v", err)
		return result
	}
	mres, ok := resp.(*kmsg.DescribeACLsResponse)
	if !ok {
		result.Err = "unexpected DescribeACLs response type"
		return result
	}
	if code := kerr.ErrorForCode(mres.ErrorCode); code != nil {
		result.Err = fmt.Sprintf("Failed to list ACLs: %v", code)
		return result
	}
	for _, res := range mres.Resources {
		for _, acl := range res.ACLs {
			result.Results = append(result.Results, map[string]any{
				"principal":      acl.Principal,
				"host":           acl.Host,
				"operation":      acl.Operation.String(),
				"resourceType":   res.ResourceType.String(),
				"resourceName":   res.ResourceName,
				"patternType":    res.ResourcePatternType.String(),
				"permissionType": acl.PermissionType.String(),
			})
		}
	}
	return result
}

// parseAcl 解析 ACL map 并构建 ACLBuilder (保持健壮性)
func (k *Service) parseAcl(acl map[string]any) (*kadm.ACLBuilder, error) {
	// 安全获取字段并验证
	principal, ok := acl["principal"].(string)
	if !ok || principal == "" {
		return nil, fmt.Errorf("invalid or missing principal")
	}
	resourceName, ok := acl["resourceName"].(string)
	if !ok {
		// 对于 CLUSTER 资源类型，resourceName 可能是 ""
		resourceType, _ := acl["resourceType"].(string)
		if strings.ToUpper(resourceType) != "CLUSTER" {
			return nil, fmt.Errorf("invalid or missing resourceName")
		}
	}
	operation, _ := acl["operation"].(string)
	permissionType, ok := acl["permissionType"].(string)
	if !ok || permissionType == "" {
		return nil, fmt.Errorf("invalid or missing permissionType")
	}
	resourceType, ok := acl["resourceType"].(string)
	if !ok || resourceType == "" {
		return nil, fmt.Errorf("invalid or missing resourceType")
	}
	host, _ := acl["host"].(string)
	if host == "" {
		host = "*"
	}

	// 转换字符串到 kadm 枚举类型
	var op kmsg.ACLOperation
	switch strings.ToUpper(operation) {
	case "ANY", "":
		op = kmsg.ACLOperationAny
	case "READ":
		op = kmsg.ACLOperationRead
	case "WRITE":
		op = kmsg.ACLOperationWrite
	case "CREATE":
		op = kmsg.ACLOperationCreate
	case "DESCRIBE":
		op = kmsg.ACLOperationDescribe
	case "DELETE":
		op = kmsg.ACLOperationDelete
	case "DESCRIBE_CONFIGS":
		op = kmsg.ACLOperationDescribeConfigs
	case "ALTER":
		op = kmsg.ACLOperationAlter
	case "ALTER_CONFIGS":
		op = kmsg.ACLOperationAlterConfigs
	case "CLUSTER_ACTION":
		op = kmsg.ACLOperationClusterAction
	case "IDEMPOTENT_WRITE":
		op = kmsg.ACLOperationIdempotentWrite
	default:
		return nil, fmt.Errorf("unsupported operation: %s", operation)
	}

	aclBuilder := kadm.NewACLs().Operations(op).ResourcePatternType(kmsg.ACLResourcePatternTypeLiteral)

	switch strings.ToUpper(permissionType) {
	case "ALLOW":
		aclBuilder.Allow(principal).AllowHosts(host)
	case "DENY":
		aclBuilder.Deny(principal).DenyHosts(host)
	default:
		return nil, fmt.Errorf("unsupported permissionType: %s", permissionType)
	}

	switch strings.ToUpper(resourceType) {
	case "TOPIC":
		aclBuilder.Topics(resourceName)
	case "GROUP":
		aclBuilder.Groups(resourceName)
	case "CLUSTER":
		// Cluster 资源名是固定的 "kafka-cluster"
		aclBuilder.Clusters()
	case "TRANSACTIONAL_ID":
		aclBuilder.TransactionalIDs(resourceName)
	case "DELEGATION_TOKEN":
		aclBuilder.DelegationTokens(resourceName)
	default:
		return nil, fmt.Errorf("unsupported resourceType: %s", resourceType)
	}

	return aclBuilder, nil
}

// CreateAcl 创建 ACL
func (k *Service) CreateAcl(acl map[string]any) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx := context.Background()

	aclBuilder, err := k.parseAcl(acl)
	if err != nil {
		result.Err = fmt.Sprintf("Failed to parse ACL: %v", err)
		return result
	}

	results, err := k.kac.CreateACLs(ctx, aclBuilder)
	if err != nil {
		result.Err = fmt.Sprintf("Failed to create ACL: %v", err)
		return result
	}

	// 检查创建结果
	for _, res := range results {
		if res.Err != nil {
			result.Err = fmt.Sprintf("Failed to create ACL: %v", res.Err)
			return result
		}
	}

	return result
}

// DeleteAcl 删除 ACL
func (k *Service) DeleteAcl(acl map[string]any) *types.ResultResp {
	result := &types.ResultResp{}
	if k.kac == nil {
		result.Err = common.PleaseSelectErr
		return result
	}
	ctx := context.Background()

	aclBuilder, err := k.parseAcl(acl)
	if err != nil {
		result.Err = fmt.Sprintf("Failed to parse ACL: %v", err)
		return result
	}

	results, err := k.kac.DeleteACLs(ctx, aclBuilder)
	if err != nil {
		result.Err = fmt.Sprintf("Failed to delete ACL: %v", err)
		return result
	}

	// 检查删除结果
	for _, res := range results {
		if res.Err != nil {
			result.Err = fmt.Sprintf("Failed to delete ACL: %v", res.Err)
			return result
		}
	}

	return result
}

// CheckAndSendAlert 检查积压并发送告警
func (k *Service) CheckAndSendAlert(alertReq types.AlertRequest, alertConfig types.AlertConfig) *types.ResultResp {
	result := &types.ResultResp{}

	if !alertConfig.Enabled {
		return result
	}

	if alertConfig.WebhookURL == "" {
		result.Err = "Webhook URL不能为空"
		return result
	}

	// 检查总积压是否超过阈值
	if alertReq.TotalLag < alertConfig.Threshold {
		fmt.Printf("总积压 %d 未超过阈值 %d", alertReq.TotalLag, alertConfig.Threshold)
		return result
	}

	// 准备告警消息
	fmt.Printf("准备告警消息: %s\n", alertConfig.MessageTemplate)
	alertMsg, err := prepareAlertMessage(alertReq, alertConfig.MessageTemplate)
	if err != nil {
		result.Err = fmt.Sprintf("准备告警消息失败: %v", err)
		return result
	}

	// 发送告警
	fmt.Printf("发送告警消息: %s\n", alertMsg)
	err = sendWebhookRequest(alertConfig.WebhookURL, alertConfig.CustomHeader, alertMsg)
	if err != nil {
		result.Err = fmt.Sprintf("发送告警失败: %v", err)
		return result
	}

	return result
}

// prepareAlertMessage 准备告警消息
func prepareAlertMessage(alertReq types.AlertRequest, template string) (string, error) {
	// 如果没有提供模板，使用默认模板
	if template == "" {
		template = `Kafka消费者组积压告警
消费者组: {{consumer_group}}
总积压: {{total_lag}}
阈值: {{threshold}}
告警时间: {{timestamp}}

Topic积压详情:
{{topics}}`
	}

	// 替换占位符
	msg := template
	msg = strings.ReplaceAll(msg, "[group]", alertReq.ConsumerGroup)
	msg = strings.ReplaceAll(msg, "[total_lag]", fmt.Sprintf("%d", alertReq.TotalLag))
	msg = strings.ReplaceAll(msg, "[threshold]", fmt.Sprintf("%d", alertReq.Threshold))
	msg = strings.ReplaceAll(msg, "[timestamp]", alertReq.Timestamp)

	// 构建topics部分
	topicsStr := ""
	for _, topic := range alertReq.TopicLags {
		topicsStr += fmt.Sprintf("  %s: %d\n", topic.TopicName, topic.Lag)
	}
	msg = strings.ReplaceAll(msg, "[topics]", topicsStr)

	return msg, nil
}

// sendWebhookRequest 使用go-resty发送webhook请求
func sendWebhookRequest(url string, customHeader string, message string) error {
	// 创建resty客户端
	client := resty.New().
		SetTimeout(10*time.Second).
		SetHeader("Content-Type", "application/json")

	// 添加自定义头
	if customHeader != "" {
		parts := strings.SplitN(customHeader, ":", 2)
		if len(parts) == 2 {
			headerName := strings.TrimSpace(parts[0])
			headerValue := strings.TrimSpace(parts[1])
			client.SetHeader(headerName, headerValue)
		}
	}

	// 发送POST请求
	resp, err := client.R().
		SetBody(message).
		Post(url)

	if err != nil {
		return fmt.Errorf("发送请求失败: %v", err)
	}

	fmt.Printf("结果: %s\n", resp.Body())

	// 检查状态码
	if resp.StatusCode() < 200 || resp.StatusCode() >= 300 {
		return fmt.Errorf("HTTP错误: %d", resp.StatusCode())
	}

	return nil
}

// ManageKafkaSCRAMUsers  添加、更新或删除 Kafka SCRAM 用户。
func (k *Service) ManageKafkaSCRAMUsers(usersToUpsert map[string]string, usersToDelete []string) (kadm.AlteredUserSCRAMs, error) {
	if k.kac == nil {
		return nil, fmt.Errorf("please connect to a cluster first")
	}
	var upserts []kadm.UpsertSCRAM
	var deletes []kadm.DeleteSCRAM
	// 3. 准备要添加或更新的用户数据 (Upserts)
	for user, password := range usersToUpsert {
		// 默认使用 SCRAM-SHA-512，迭代次数为 4096
		upsert := kadm.UpsertSCRAM{
			User:       user,
			Password:   password,
			Mechanism:  kadm.ScramSha512,
			Iterations: 4096,
		}
		upserts = append(upserts, upsert)
	}

	// 4. 准备要删除的用户数据 (Deletes)
	for _, user := range usersToDelete {
		// 删除时，需要指定要删除的凭据机制
		del := kadm.DeleteSCRAM{
			User:      user,
			Mechanism: kadm.ScramSha512, // 假设删除的是 SHA-512 的凭据
		}
		// 如果你的环境中同时存在 SHA-256 和 SHA-512 的同名用户，
		// 你可能需要更复杂的逻辑来决定删除哪一个，或者两个都删除。
		// 例如：
		// deletes = append(deletes, kadm.DeleteSCRAM{User: user, Mechanism: kadm.ScramSha256})
		// deletes = append(deletes, kadm.DeleteSCRAM{User: user, Mechanism: kadm.ScramSha512})
		deletes = append(deletes, del)
	}

	// 5. 调用 AlterUserSCRAMs 函数
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	// 同时传入删除列表和更新/插入列表
	results, err := k.kac.AlterUserSCRAMs(ctx, deletes, upserts)
	if err != nil {
		return nil, fmt.Errorf("修改 SCRAM 用户失败: %v", err)
	}

	return results, nil
}
