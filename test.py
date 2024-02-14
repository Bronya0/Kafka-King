#!/usr/bin/env python
# -*-coding:utf-8 -*-
import datetime
import json

from kafka import KafkaProducer, KafkaAdminClient, KafkaClient, KafkaConsumer
from kafka.cluster import ClusterMetadata
from kafka.protocol.admin import DescribeConfigsResponse
from kafka.protocol.api import Response
from kafka.structs import BrokerMetadata, TopicPartition

bootstrap_servers = ['10.19.50.46:9092']
# bootstrap_servers = ['127.0.0.1:9092']
# admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
# client = KafkaClient(bootstrap_servers=bootstrap_servers)

# 生产者绩效指标。
# p = KafkaProducer(bootstrap_servers=bootstrap_servers)
# print(json.dumps(p.metrics()))
# for i in range(10):
#     p.send('test', value=datetime.datetime.now().strftime('%Y%m%D%H%M%S').encode())


# 全部topic
c = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
# 获取集群的元数据
# cluster_metadata = c.describe_cluster()

# {"throttle_time_ms": 0, "brokers": [{"node_id": 1, "host": "DESKTOP-7QTQFHC", "port": 9093, "rack": null}], "cluster_id": "VEVW-Mc8R-2XWeS0MGOGew", "controller_id": 1}
# print(json.dumps(cluster_metadata))

# 创建一个 Kafka 消费者，但不需要订阅任何特定主题
# consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers, group_id="group1")
#
# # 为每个 Topic 获取其所有分区和偏移量
# topic_offsets = {}
# # all_topics = c.list_topics()
# all_topics = ['test1']
#
# print(c.list_consumer_groups())
# for topic in all_topics:
#     print(topic)
#     # 每个主题下的每个分区的lag值求和，只按topic进行统计
#     topic_lag = 0
#     for partition in consumer.partitions_for_topic(topic):
#         tp = TopicPartition(topic=topic, partition=partition)
#         # 最后一次提交的偏移量
#         last_committed = consumer.committed(tp)
#         if last_committed is None:
#             last_committed = 0
#         # 下一个写进日志的消息的偏移量
#         end_offsets = consumer.end_offsets([tp])[tp]
#         topic_lag += end_offsets - last_committed
#         print(topic, last_committed, end_offsets)

#
# 获取所有主题列表


# print(c.describe_configs())
# print(c._get_cluster_metadata())
# print(c.describe_cluster())
# print(json.dumps(c.describe_topics()))
print(json.dumps(c.list_consumer_groups()))  # [["query-gateway-group", "consumer"],
print(c.list_consumer_group_offsets(group_id='group1'))  # TopicPartition字典：k：topic+分区，v：end_offset
group_ids = [i[0] for i in c.list_consumer_groups()]
print(c.describe_consumer_groups(group_ids=group_ids))   # 查看多个消费者组的state、protocol、members（MemberInformation\client_id\client_host）

# print(c.describe_configs())
# print(c.describe_acls())
# print(c.describe_consumer_groups())