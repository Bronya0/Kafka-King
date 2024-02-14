#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/31 16:16
@File    : kafka_service.py
@Project : kafka-king
@Desc    : 
"""

import logging
import traceback
from collections import defaultdict
from typing import Optional

from kafka import KafkaAdminClient, KafkaClient, KafkaConsumer, TopicPartition, KafkaProducer
from kafka.admin import NewPartitions

# 配置日志输出
logging.basicConfig(level=logging.INFO)


class TopicConfig:
    def __int__(self, name: str, num_partitions: int = 1, replication_factor: int = 1):
        self.name = name
        self.num_partitions = num_partitions
        self.replication_factor = replication_factor


class KafkaService:
    def __init__(self):
        self.bootstrap_servers = None
        self.kc: Optional[KafkaClient] = None
        self.kac: Optional[KafkaAdminClient] = None

    def set_bootstrap_servers(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.kac = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

    def new_client(self, bootstrap_servers: list):

        # 测试连接
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
            topics = admin_client.list_topics()
            admin_client.close()
            return True
        except Exception as e:
            return False

        # 如果只是检查连接，不需要发送消息，可以省略消息发送的部分

    def get_brokers(self):
        """
            {
              "throttle_time_ms": 0,
              "brokers": [
                {
                  "node_id": 1,
                  "host": "DESKTOP-C",
                  "port": 9092,
                  "rack": null
                }
              ],
              "cluster_id": "VERS",
              "controller_id": 1
            }
        """
        cluster_metadata = self.kac.describe_cluster()
        # 尝试猜测 Kafka 代理的版本
        kc = KafkaClient(bootstrap_servers=self.bootstrap_servers)
        api_version = kc.check_version()
        kc.close()
        return cluster_metadata, api_version

    def get_topics(self):
        describe_topics = self.kac.describe_topics()
        describe_topics = sorted(describe_topics, key=lambda d: d['topic'])
        return describe_topics

    def get_groups(self):
        """
        列出集群已知的所有消费者组。
        这将返回消费者列表。元组由消费者组名称和消费者组协议类型组成。
        """
        _consumer_groups = self.kac.list_consumer_groups()
        consumer_groups = [i[0] for i in _consumer_groups]
        return consumer_groups

    def get_topic_offsets(self, topics, group_id):
        consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers, group_id=group_id)

        topic_lag = {}
        topic_offset = defaultdict(dict)
        for topic in topics:
            _lag = 0
            for partition in consumer.partitions_for_topic(topic):
                tp = TopicPartition(topic=topic, partition=partition)
                # 最后一次提交的偏移量
                last_committed = consumer.committed(tp)
                if last_committed is None:
                    last_committed = 0
                # 下一个写进日志的消息的偏移量
                end_offsets = consumer.end_offsets([tp])[tp]
                _lag += end_offsets - last_committed
                topic_offset[topic][partition] = [last_committed, end_offsets, end_offsets - last_committed]
            topic_lag[topic] = _lag
        return topic_offset, topic_lag

    def create_partitions(self, topic, old_num, new_num):
        """
        为现有主题创建附加分区。
         参数：
        topic_partitions – 主题名称字符串到 NewPartition 对象的映射。
        timeout_ms – 代理返回之前等待创建新分区的毫秒数。
        validate_only – 如果为 True，则实际上不创建新分区。默认值：假
         返回：
        CreatePartitionsResponse 类的适当版本。
        """
        topic_partitions = {topic: NewPartitions(total_count=old_num + new_num)}
        try:
            res = self.kac.create_partitions(topic_partitions)
            return True
        except Exception as e:
            traceback.print_exc()
        return False

    def send_msgs(self, topic, msg: bytes, enable_gzip=False, msg_multiplier=1, msg_key=None):
        """
        send msgs发送消息
        """
        config = {
            "bootstrap_servers": self.bootstrap_servers,
        }
        if enable_gzip:
            config['compression_type'] = 'gzip'

        p = KafkaProducer(**config)

        for i in range(msg_multiplier):
            p.send(topic=topic, value=msg, key=msg_key)
        p.flush()
        p.close()


