#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/13 17:51
@File    : consumer.py
@Project : kafka-king
@Desc    : 
"""
from kafka import KafkaConsumer
import json
import time

topics = ['test']
bootstrap_servers = ['10.19.50.46:9092']

consumer = KafkaConsumer(*topics,
                         group_id='group1',
                         enable_auto_commit=False,
                         bootstrap_servers=bootstrap_servers)

s1 = time.time()
for message in consumer:
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value.decode()))
    consumer.commit()
