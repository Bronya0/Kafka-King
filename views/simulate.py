#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/14 10:50
@File    : simulate.py
@Project : kafka-king
@Desc    : 
"""
import flet as ft

from common import dd_common_configs


class Simulate(object):

    def __init__(self, KafkaService):
        self.describe_topics_map = None
        self.describe_topics = None
        self.KafkaService = KafkaService

        # producer tab's topic Dropdown
        self.producer_topic_dd = ft.Dropdown(
            label="topic",
            # on_change=self.click_partition_topic_dd_onchange,
            **dd_common_configs
        )

        # producer tab's enable compress switch
        self.producer_compress_switch = ft.Switch(label="开启消息gzip压缩", value=False)

        # producer tap
        self.producer_tab = ft.Tab(
            icon=ft.icons.TRENDING_UP, text="Producer", content=ft.Container()
        )

        # consumer tab's topic Dropdown
        self.consumer_topic_dd = ft.Dropdown(
            label="topic",
            **dd_common_configs
        )

        # consumer groups Dropdown
        self.consumer_groups_dd = ft.Dropdown(
            label="consumer groups",
            **dd_common_configs
        )

        # consumer tap
        self.consumer_tab = ft.Tab(
            icon=ft.icons.TOLL, text="Consumer", content=ft.Container()
        )

        # all in one
        self.tab = ft.Tabs(
            animation_duration=300,
            tabs=[
                self.producer_tab,
                self.consumer_tab,
            ],
            expand=1,
        )

        self.controls = [
            self.tab,
        ]

    def init(self):
        self.describe_topics = self.KafkaService.get_topics()
        self.describe_topics_map = {i['topic']: i for i in self.describe_topics}

        _topic_lst = self.describe_topics_map.keys()

        # init topic dd
        self.producer_topic_dd.options = [ft.dropdown.Option(text=i) for i in _topic_lst]
        self.consumer_topic_dd.options = [ft.dropdown.Option(text=i) for i in _topic_lst]

        # 消费组初始化
        self.consumer_groups_dd.options = [ft.dropdown.Option(text=i) for i in self.KafkaService.get_groups()]

        # init producer tab
        self.producer_tab.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.producer_topic_dd,
                ]),
            ],
                scroll=ft.ScrollMode.ALWAYS,
            ),
            alignment=ft.alignment.top_left,
            padding=10,
        )

        # init consumer tab
        self.consumer_tab.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.consumer_topic_dd,
                    self.consumer_groups_dd,
                ]),
            ],
                scroll=ft.ScrollMode.ALWAYS,
            ),
            alignment=ft.alignment.top_left,
            padding=10,
        )