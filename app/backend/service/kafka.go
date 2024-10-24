package kafka

import (
	"fmt"
	"github.com/IBM/sarama"
	"sync"
	"time"
)

const KingGroup = "kafka-king-group"

type TopicConfig struct {
	Name              string
	NumPartitions     int32
	ReplicationFactor int16
}

type Service struct {
	connectName string
	conn        map[string]string
	kac         sarama.ClusterAdmin
	consumer    sarama.Consumer
	mutex       sync.Mutex
}

func NewKafkaService() *Service {
	return &Service{
		conn: make(map[string]string),
	}
}

func (k *Service) SetConnect(connectName string, conn map[string]string) error {
	k.mutex.Lock()
	defer k.mutex.Unlock()

	k.conn = conn
	k.connectName = connectName

	config := sarama.NewConfig()
	config.Version = sarama.V2_8_0_0 // Adjust version as needed

	// Convert conn map to proper config
	// Add necessary configurations from conn map to sarama config

	admin, err := sarama.NewClusterAdmin([]string{conn["bootstrap.servers"]}, config)
	if err != nil {
		k.kac = nil
		k.consumer = nil
		return err
	}
	k.kac = admin

	return k.newConsumer()
}

func (k *Service) newConsumer() error {
	config := sarama.NewConfig()
	config.Consumer.Offsets.Initial = sarama.OffsetOldest
	config.Consumer.MaxProcessingTime = 10 * time.Second

	consumer, err := sarama.NewConsumer([]string{k.conn["bootstrap.servers"]}, config)
	if err != nil {
		return err
	}
	k.consumer = consumer
	fmt.Println("Internal consumer created successfully")
	return nil
}

func (k *Service) NewClient(connectName string, conn map[string]string) (bool, error) {
	config := sarama.NewConfig()
	admin, err := sarama.NewClusterAdmin([]string{conn["bootstrap.servers"]}, config)
	if err != nil {
		return false, err
	}
	defer admin.Close()

	topics, err := admin.ListTopics()
	if err != nil {
		return false, err
	}
	_ = topics
	return true, nil
}

func (k *Service) GetBrokers() (map[string]interface{}, string) {
	if k.kac == nil {
		return nil, ""
	}

	brokers, _, err := k.kac.DescribeCluster()
	if err != nil {
		return nil, ""
	}

	brokerInfo := make([]map[string]interface{}, 0)
	for _, broker := range brokers {
		brokerInfo = append(brokerInfo, map[string]interface{}{
			"node_id": broker.ID(),
			"host":    broker.Addr(),
			"rack":    broker.Rack(),
		})
	}

	clusterInfo := map[string]interface{}{
		"brokers":       brokerInfo,
		"cluster_id":    "", // Sarama doesn't provide cluster ID directly
		"controller_id": 0,  // Would need additional logic to determine controller
	}

	return clusterInfo, "2.8.0" // Version would need to be determined differently
}

func (k *Service) GetTopics() ([]map[string]interface{}, error) {
	if k.kac == nil {
		return nil, fmt.Errorf("admin client not initialized")
	}

	topics, err := k.kac.ListTopics()
	if err != nil {
		return nil, err
	}

	result := make([]map[string]interface{}, 0)
	for topicName, topicDetail := range topics {
		result = append(result, map[string]interface{}{
			"topic":              topicName,
			"partition_count":    topicDetail.NumPartitions,
			"replication_factor": topicDetail.ReplicationFactor,
			"ReplicaAssignment":  topicDetail.ReplicaAssignment,
		})
	}

	return result, nil
}

func (k *Service) GetGroups() ([]string, error) {
	if k.kac == nil {
		return nil, fmt.Errorf("admin client not initialized")
	}

	groups, err := k.kac.ListConsumerGroups()
	if err != nil {
		return nil, err
	}

	result := make([]string, 0)
	for groupName := range groups {
		result = append(result, groupName)
	}

	return result, nil
}

func (k *Service) GetTopicOffsets(topics []string, groupID string) (map[string]map[int32][]int64, map[string][]int64, error) {
	topicOffset := make(map[string]map[int32][]int64)
	topicLag := make(map[string][]int64)

	var consumer sarama.Consumer
	var err error

	if groupID != "" && groupID != KingGroup {
		config := sarama.NewConfig()
		consumer, err = sarama.NewConsumer([]string{k.conn["bootstrap.servers"]}, config)
	} else {
		consumer = k.consumer
		if consumer == nil {
			err = k.newConsumer()
			if err != nil {
				return nil, nil, err
			}
			consumer = k.consumer
		}
	}

	if err != nil {
		return nil, nil, err
	}

	for _, topic := range topics {
		partitions, err := consumer.Partitions(topic)
		if err != nil {
			continue
		}

		topicOffset[topic] = make(map[int32][]int64)
		var totalEndOffset, totalCommitted int64

		for _, partition := range partitions {
			pc, err := consumer.ConsumePartition(topic, partition, sarama.OffsetOldest)
			if err != nil {
				continue
			}

			committed := pc.HighWaterMarkOffset()
			endOffset, err := k.getLatestOffset(topic, partition)
			if err != nil {
				continue
			}

			lag := endOffset - committed
			topicOffset[topic][partition] = []int64{committed, endOffset, lag}

			totalEndOffset += endOffset
			totalCommitted += committed

			pc.Close()
		}

		topicLag[topic] = []int64{totalEndOffset, totalCommitted}
	}

	return topicOffset, topicLag, nil
}

func (k *Service) getLatestOffset(topic string, partition int32) (int64, error) {
	client, err := sarama.NewClient([]string{k.conn["bootstrap.servers"]}, sarama.NewConfig())
	if err != nil {
		return 0, err
	}
	defer client.Close()

	offset, err := client.GetOffset(topic, partition, sarama.OffsetNewest)
	if err != nil {
		return 0, err
	}
	return offset, nil
}
