#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/13 17:51
@File    : producer.py
@Project : kafka-king
@Desc    : 
"""
# import datetime
#
# from kafka import KafkaProducer
#
# bootstrap_servers = ['10.19.50.46:9092']
# # bootstrap_servers = ['127.0.0.1:9092']
# # admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
# # client = KafkaClient(bootstrap_servers=bootstrap_servers)
#
# # 生产者绩效指标。
# p = KafkaProducer(bootstrap_servers=bootstrap_servers)
# # print(json.dumps(p.metrics()))
# for i in range(1):
#     res = p.send('test', value=datetime.datetime.now().strftime('%Y%m%D%H%M%S').encode())
#     res.get()
