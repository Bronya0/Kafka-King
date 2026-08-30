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
	"bytes"
	"compress/gzip"
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"testing"
	"time"

	"github.com/twmb/franz-go/pkg/kadm"
	"github.com/twmb/franz-go/pkg/kgo"
)

// 引入 testing 包

// integrationGuard 集成测试需要真实 Kafka 集群；默认跳过，设置 KAFKA_KING_INTEGRATION=1 才运行
func integrationGuard(t *testing.T) {
	t.Helper()
	if os.Getenv("KAFKA_KING_INTEGRATION") == "" {
		t.Skip("set KAFKA_KING_INTEGRATION=1 to run integration tests (require a live Kafka cluster)")
	}
}

func TestNewKafkaService2(t *testing.T) { // 功能测试以 `Test` 前缀命名
	integrationGuard(t)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	//seeds := []string{"localhost:9092"}
	seeds := []string{"192.168.1.100:9092"}

	// 2. 自定义TLS配置
	// 加载CA证书
	//caCert, err := os.ReadFile("ca.pem")
	//caCertPool := x509.NewCertPool()
	//caCertPool.AppendCertsFromPEM(caCert)
	//// 加载客户端证书和私钥
	//cert, err := tls.LoadX509KeyPair("client-cert.pem", "client-key.pem")
	//tlsConfig := &tls.Config{
	//	RootCAs:      caCertPool,
	//	Certificates: []tls.Certificate{cert},
	//	MinVersion:   tls.VersionTLS12,
	//}

	//创建客户端
	//配置千万不能冲突
	client, err := kgo.NewClient(
		kgo.SeedBrokers(seeds...),
		//kgo.SASL(plain.Auth{
		//	User: "admin",
		//	Pass: "admin-secret",
		//}.AsMechanism()),
		//kgo.ProducerBatchCompression(kgo.GzipCompression()),
		kgo.ConsumeTopics("1"),
		kgo.ConsumeResetOffset(kgo.NewOffset().AtStart()),
		//kgo.ConsumerGroup("1"),
		//kgo.Balancers(kgo.CooperativeStickyBalancer()),
	)
	if err != nil {
		log.Fatal(err)
	}
	//包装admin客户端
	admin := kadm.NewClient(client)
	defer client.Close()
	defer admin.Close()
	//生产消息
	st := time.Now()
	datas := make([]*kgo.Record, 0)
	for i := 0; i < 1000; i++ {
		bt, _ := gzipCompress([]byte(time.Now().Format(time.DateTime)))
		datas = append(datas, &kgo.Record{
			Topic: "gzip",
			//Value: []byte(time.Now().Format(time.DateTime)),
			Value: bt,
		})
	}
	client.ProduceSync(ctx, datas...)

	fmt.Printf("耗时：%.4f秒\n", time.Now().Sub(st).Seconds())

	////消费消息。订阅也可以在创建客户端的时候做
	//client.AddConsumeTopics("1")

	// 必须关闭client
	fetches := client.PollRecords(ctx, 10)

	if fetches.IsClientClosed() {
		panic("Client Closed")
	}
	if errors.Is(ctx.Err(), context.DeadlineExceeded) {
		panic("Consume Timeout")
	}
	if errs := fetches.Errors(); len(errs) > 0 {
		panic(fmt.Sprint(errs))
	}
	for _, record := range fetches.Records() {
		fmt.Println(record.Offset, string(record.Value))
	}
	//提交offset
	//if err := client.CommitUncommittedOffsets(ctx); err != nil {
	//	log.Fatalf("提交offsets失败: %v", err)
	//}

	client.Close()
	admin.Close()

	////读取offset
	//res2, err := admin.FetchOffsetsForTopics(ctx, "g1", "1")
	//if err != nil {
	//	log.Fatal(err)
	//}
	//newMap := map[string]map[int32]any{}
	//for k1, v := range res2.Offsets() {
	//	if _, ok := newMap[k1]; !ok {
	//		newMap[k1] = make(map[int32]any)
	//	}
	//	for k2, v2 := range v {
	//		//fmt.Printf("%+v\n", v2)
	//		m := common.StructToMap(v2)
	//		newMap[k1][k2] = m
	//	}
	//}
	//fmt.Printf("%+v\n", newMap)

	//topics, err := admin.ListTopics(ctx)
	//fmt.Printf("%+v", topics)

	//fmt.Println(admin.ListBrokers(ctx))

	//fmt.Println(admin.ListGroups(ctx))

	//fmt.Println(admin.ListTopicsWithInternal(ctx))

	//res, _ := admin.ListStartOffsets(ctx, "1")
	//fmt.Printf("%+v\n", res)
	//
	//res, _ = admin.ListCommittedOffsets(ctx, "1")
	//fmt.Printf("%+v\n", res)
	//
	//res, _ = admin.ListEndOffsets(ctx, "1")
	//fmt.Printf("%+v\n", res)

	//ks.CreateTopics([]map[string]any{
	//	{
	//		"topic":             "test3",
	//		"numPartitions":     2,
	//		"replicationFactor": 1,
	//		"cleanupPolicy":     "delete",
	//		"retentionMs":       "604800000",
	//	},
	//})
	//res := ks.GetBrokers().Result

	//fmt.Printf("%+v", res["brokers"])
	//
	//fmt.Println(ks.CreatePartitions([]string{"test3"}, 1))
	//fmt.Println(ks.GetTopics())
	//fmt.Println(ks.GetGroups())
	//fmt.Println(ks.GetTopicConfig("test3"))
	//fmt.Println(ks.DeleteTopic([]string{"test1"}))
	//fmt.Println(ks.DescribeTopic([]string{"test3"}))
	//fmt.Println(ks.AlterTopicConfig("test3", map[string]*string{"retention.ms": ptr("60480")}))
	//fmt.Println(ks.GetTopicConfig("test3"))

	//map[g1:{Group:g1 Coordinator:{NodeID:0 Port:9092 Host:DESKTOP-7QTQFHC.mshome.net Rack:<nil> _:{}} State:Stable ProtocolType:consumer Protocol:cooperative-sticky
	//Members:[{MemberID:kgo-eb77103b-d127-4f0d-9159-6bdc92030cd1 InstanceID:<nil> ClientID:kgo ClientHost:/192.168.160.1 Join:{i:0xc000032960} Assigned:{i:0xc000284000}}] Err:<nil>}]
	//res, _ := admin.DescribeGroups(ctx, "g1")
	//fmt.Printf("%+v\n", res)
}
func gzipCompress(data []byte) ([]byte, error) {
	var buf bytes.Buffer
	gzipWriter := gzip.NewWriter(&buf) // Create a gzip writer that writes to the buffer

	_, err := gzipWriter.Write(data) // Write the data to the gzip writer
	if err != nil {
		return nil, fmt.Errorf("gzip write error: %w", err)
	}

	err = gzipWriter.Close() // Important: Close the writer to flush and finalize the gzip stream
	if err != nil {
		return nil, fmt.Errorf("gzip close error: %w", err)
	}

	return buf.Bytes(), nil // Return the compressed data from the buffer
}

func TestGroupMembers(t *testing.T) {
	integrationGuard(t)
	s := NewKafkaService()
	s.SetConnect("dsd", map[string]any{
		"name":              "debian",
		"bootstrap_servers": "192.168.1.100:9092",
	}, false)
	gs := s.GetGroups()
	fmt.Printf("%+v\n", gs)

	res := s.GetGroupMembers([]string{"111"})
	fmt.Printf("%+v", res)
}

func TestConsume(t *testing.T) {
	integrationGuard(t)
	s := NewKafkaService()
	s.SetConnect("dsd", map[string]any{
		"name":              "debian",
		"bootstrap_servers": "192.168.1.100:9092",
		"tls":               "disable",
		"skipTLSVerify":     "",
		"tls_cert_file":     "",
		"tls_key_file":      "",
		"tls_ca_file":       "", "sasl": "disable", "sasl_mechanism": "PLAIN", "sasl_user": "", "sasl_pwd": "", "kerberos_user_keytab": "", "kerberos_krb5_conf": "", "Kerberos_user": "", "Kerberos_realm": "", "kerberos_service_name": "",
	}, false)

	res := s.Consumer("1", "__kafka_king_auto_generate__", 5, 1000, "", "read_committed", false, true, 1746879189000, 0, "none")
	fmt.Printf("%+v", res)
}
func TestAcls(t *testing.T) {
	integrationGuard(t)

	svc := NewKafkaService()
	svc.SetConnect("test", map[string]any{
		"bootstrap_servers": ":9092",
	}, false)

	//rule := map[string]any{
	//	"principal":    "User:*",
	//	"resourceType": "TOPIC",
	//	//"permissionType": "ALLOW",
	//	"permissionType": "DENY",
	//	"resourceName":   "1",
	//	"operation":      "READ",
	//	"host":           "*",
	//}

	//fmt.Println(svc.CreateAcl(rule))

	fmt.Println(svc.GetAcls().Results)

	//fmt.Println(svc.DeleteAcl(rule))
}
