#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/31 16:16
@File    : kafka_service.py
@Project : kafka-king
@Desc    : 
"""
import copy
import logging
import time
import traceback
from collections import defaultdict
from typing import Optional, List

from kafka import KafkaAdminClient, KafkaClient, KafkaConsumer, TopicPartition, KafkaProducer
from kafka.admin import NewPartitions, ConfigResource, ConfigResourceType
from kafka.protocol.admin import DescribeConfigsResponse_v2
from kafka.structs import GroupInformation

from service.common import KAFKA_KING_GROUP

# 配置日志输出
logging.basicConfig(level=logging.INFO)


class TopicConfig:
    def __int__(self, name: str, num_partitions: int = 1, replication_factor: int = 1):
        self.name = name
        self.num_partitions = num_partitions
        self.replication_factor = replication_factor


class KafkaService:
    def __init__(self):
        self.connect_name = None
        self.SASL_PARAM = None
        self.kac: Optional[KafkaAdminClient] = None
        self.consumer = None

    def set_connect(self, connect_name, bootstrap_servers: list, sasl_plain_username, sasl_plain_password):
        SASL_PARAM = {"bootstrap_servers": bootstrap_servers}
        if sasl_plain_username and sasl_plain_password:
            SASL_PARAM.update({
                "security_protocol": 'SASL_PLAINTEXT',
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": sasl_plain_username,
                "sasl_plain_password": sasl_plain_password,
            })
        self.SASL_PARAM = SASL_PARAM
        self.connect_name = connect_name
        # 此处异常要重置kac，否则会复用之前的历史连接
        try:
            self.kac = KafkaAdminClient(**SASL_PARAM)
            self.new_consumer()
        except Exception as e:
            self.kac = None
            self.consumer = None
            raise e

    def new_consumer(self):
        self.consumer = KafkaConsumer(
            group_id=KAFKA_KING_GROUP,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            max_poll_records=10000,
            **self.SASL_PARAM,
        )
        print("内置消费者创建成功")

    def new_client(self, bootstrap_servers: list, sasl_plain_username, sasl_plain_password):
        SASL_PARAM = {"bootstrap_servers": bootstrap_servers}
        if sasl_plain_username and sasl_plain_password:
            SASL_PARAM.update({
                "security_protocol": 'SASL_PLAINTEXT',
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": sasl_plain_username,
                "sasl_plain_password": sasl_plain_password,
            })
        # 测试连接
        try:
            admin_client = KafkaAdminClient(**SASL_PARAM)
            topics = admin_client.list_topics()
            admin_client.close()
            return True, None
        except Exception as e:
            return False, str(e)

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
        kc = KafkaClient(**self.SASL_PARAM)
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
        print(topics, group_id)
        if group_id is not None and group_id != KAFKA_KING_GROUP:
            print(f"创建消费者:{group_id}")
            consumer = KafkaConsumer(**self.SASL_PARAM, group_id=group_id)
        else:
            print(f"使用自带消费者:{KAFKA_KING_GROUP}")
            consumer = self.consumer
            if consumer is None:
                self.new_consumer()
        topic_lag, topic_end_and_commit_offset = {}, {}
        topic_offset = defaultdict(dict)
        for topic in topics:
            _lag = 0
            partitions = consumer.partitions_for_topic(topic)
            if partitions is None:
                continue
            topic_end_offsets = 0
            topic_last_committed = 0
            for partition in partitions:
                tp = TopicPartition(topic=topic, partition=partition)
                # 最后一次提交的偏移量
                last_committed = consumer.committed(tp)
                if last_committed is None:
                    last_committed = 0
                # 下一个写进日志的消息的偏移量
                end_offsets = consumer.end_offsets([tp])[tp]

                topic_end_offsets += end_offsets
                topic_last_committed += last_committed

                _lag += end_offsets - last_committed
                topic_offset[topic][partition] = [last_committed, end_offsets, end_offsets - last_committed]
            topic_lag[topic] = [topic_end_offsets, topic_last_committed]
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
            return True, None
        except Exception as err:
            traceback.print_exc()
            return False, str(err)

    def send_msgs(self, topic, msg: bytes, enable_gzip=False, msg_multiplier=1, msg_key=None, headers_lst=None, **kwargs):
        """
        send msgs发送消息
        """
        config: dict = copy.copy(self.SASL_PARAM)
        config.update(kwargs)
        if enable_gzip:
            config['compression_type'] = 'gzip'

        p = KafkaProducer(**config)

        for i in range(msg_multiplier):
            p.send(topic=topic, value=msg, key=msg_key, headers=headers_lst)
        p.flush()
        p.close()

    def fetch_msgs(self, topic, group_id, size=10, timeout=10):
        """
        拉取消息
        """
        if not self.consumer:
            print("使用内置消费者")
            self.new_consumer()

        print(f"订阅主题:{topic}")
        self.consumer.subscribe(topics=[topic])
        # 计数器
        n = 0
        msgs = ""
        ori_msgs_lst = []
        st = time.time()
        while n < size:
            # timeout_ms：一直拉不到数据时，最多等待的时间，超时直接返回空字典
            res: dict = self.consumer.poll(timeout_ms=3000, max_records=size)

            for tp, records in res.items():
                for record in records:
                    headers = ""
                    try:
                        print(record.headers)
                        for header in record.headers:
                            key = header[0]  # 解码头部键
                            value = header[1].decode('utf-8')  # 解码头部值
                            headers += f"{key}:{value},"

                        msgs += "{}. 偏移:{}, 分区:{}, 键:{}, header:{} 内容:{}\n".format(
                            n, record.offset,
                            record.partition,
                            record.key.decode('utf-8') if record.key is not None else "",
                            headers,
                            record.value.decode('utf-8') if record.value is not None else ""
                        )
                    except:
                        msgs += "{}. 偏移:{}, 分区:{}, 键:{}, header:{}, 内容:{}\n".format(
                            n, record.offset,
                            record.partition,
                            record.key,
                            headers,
                            "无法utf-8解码"
                        )
                    ori_msgs_lst.append(record.value)
                    n += 1
            self.consumer.commit()
            if time.time() - st >= timeout:
                break

        return msgs, ori_msgs_lst

    def get_configs(self, res_type, name):
        """
        获取topic或broker的配置
        """
        name = str(name)
        if res_type == "topic":
            config_resource = ConfigResource(ConfigResourceType.TOPIC, name)
        elif res_type == "broker":
            config_resource = ConfigResource(ConfigResourceType.BROKER, name)
        else:
            return
        res_lst = self.kac.describe_configs([config_resource])
        res: DescribeConfigsResponse_v2 = res_lst[0]
        configs = res.to_object()['resources'][0]['config_entries']
        configs = sorted(configs, key=lambda item: item['config_names'])
        return configs

    def describe_groups(self, groups):
        """
        通过组名获取组信息和成员信息
        """
        group_descriptions: List[GroupInformation] = self.kac.describe_consumer_groups(groups)
        return group_descriptions


kafka_service = KafkaService()
