#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/14 10:50
@File    : simulate.py
@Project : kafka-king
@Desc    : 
"""
import time
import traceback

import flet as ft
from flet_core import ControlEvent

from common import dd_common_configs, S_Button, open_snack_bar
from service.kafka_service import kafka_service


class Simulate(object):

    def __init__(self):
        self.describe_topics_map = None
        self.describe_topics = None
        self.__kafka_king_group = "__kafka_king_group"
        self.kafka_fetch_timeout = 10

        if not kafka_service.kac:
            raise Exception("请先选择一个kafka连接！")

        # producer tab's topic Dropdown
        self.producer_topic_dd = ft.Dropdown(
            label="topic",
            # on_change=self.click_partition_topic_dd_onchange,
            **dd_common_configs
        )

        # msg key
        self.producer_msg_key_input = ft.TextField(
            label="msg key",
            width=200, height=30, text_size=14, content_padding=10
        )

        # 消息输入框
        self.producer_send_input = ft.TextField(
            multiline=True,
            keyboard_type=ft.KeyboardType.MULTILINE,
            max_length=1000,
            min_lines=8,
            max_lines=8,
            hint_text="支持字符串，可以输入String、Json等消息。"
        )

        # 消息倍数
        self.producer_slider = ft.Slider(min=1, max=10000, divisions=20, label="×{value}", value=1)

        # send button
        self.producer_send_button = S_Button(
            text="Send Message",
            on_click=self.click_send_msg,
        )

        # producer tab's enable compress switch
        self.producer_compress_switch = ft.Switch(label="开启gzip压缩：", label_position=ft.LabelPosition.LEFT,
                                                  value=False)

        # producer tap
        self.producer_tab = ft.Tab(
            icon=ft.icons.TRENDING_UP, text="Producer", content=ft.Container()
        )

        # consumer tab's topic Dropdown
        self.consumer_topic_dd = ft.Dropdown(
            label="choose topic",
            **dd_common_configs
        )

        # consumer fetch size
        self.consumer_fetch_size_input = ft.TextField(
            label="fetch size",
            value="10",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200, height=30, text_size=14, content_padding=10
        )

        # consumer groups input
        # self.consumer_groups_input = ft.TextField(
        #     label="new consumer group",
        #     width=200, height=30, text_size=14, content_padding=10
        # )

        # consumer fetch msg button
        self.consumer_fetch_msg_button = S_Button(
            text="Fetch Message",
            on_click=self.click_fetch_msg,
        )

        # consumer fetch msg text
        self.consumer_fetch_msg_body = ft.Text(
            selectable=True,
            size=14,
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
        self.describe_topics = kafka_service.get_topics()
        self.describe_topics_map = {i['topic']: i for i in self.describe_topics}

        _topic_lst = []
        for i in self.describe_topics:
            if i['is_internal'] is True:
                continue
            _topic_lst.append(i['topic'])

        # init topic dd
        self.producer_topic_dd.options = [ft.dropdown.Option(text=i) for i in _topic_lst]
        self.consumer_topic_dd.options = [ft.dropdown.Option(text=i) for i in _topic_lst]

        # 消费组初始化
        # self.consumer_groups_dd.options = [ft.dropdown.Option(text=i) for i in kafka_service.get_groups()]

        # init producer tab
        self.producer_tab.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.producer_topic_dd,
                    self.producer_msg_key_input,
                ]),
                ft.Markdown(value="""# 输入单条消息内容"""),
                # msg input
                self.producer_send_input,
                # enable gzip
                self.producer_compress_switch,
                # msg multiplier
                ft.Text("消息发送倍数：默认*1"),
                self.producer_slider,
                # msg send button
                self.producer_send_button
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
                    self.consumer_fetch_size_input,
                    # self.consumer_groups_dd,
                    # ft.Text(" OR "),
                    # self.consumer_groups_input,
                    ft.Text(f"Group:  {self.__kafka_king_group}"),
                    ft.Text(f"FetchTimeout:  {self.kafka_fetch_timeout}")
                ]),
                self.consumer_fetch_msg_button,
                self.consumer_fetch_msg_body,
            ],

                scroll=ft.ScrollMode.ALWAYS,
            ),
            alignment=ft.alignment.top_left,
            padding=10,
        )

    def click_send_msg(self, e: ControlEvent):
        """
        发送消息
        乘以倍数，and 是否压缩
        """
        topic = self.producer_topic_dd.value
        msg = self.producer_send_input.value
        enable_gzip = self.producer_compress_switch.value
        msg_multiplier = int(self.producer_slider.value)
        msg_key = self.producer_msg_key_input.value.rstrip()

        st = time.time()
        res = "发送成功"
        try:
            kafka_service.send_msgs(
                topic=topic,
                msg=msg.encode('utf-8'),
                enable_gzip=enable_gzip,
                msg_multiplier=msg_multiplier,
                msg_key=msg_key.encode('utf-8'),
            )
        except Exception as e_:
            traceback.print_exc()
            res = f"发送失败：{e_}"
        et = time.time() - st
        res += f"\n发送耗时{et} s"
        open_snack_bar(e.page, e.page.snack_bar, res)

    def click_fetch_msg(self, e: ControlEvent):
        """
        根据topic 和 group、size、拉取消息
        """
        err = None
        topic = self.consumer_topic_dd.value
        if topic is None:
            err = "请选择topic"
        group = self.__kafka_king_group
        size = self.consumer_fetch_size_input.value
        try:
            size = int(size)
            if size <= 0:
                err = "size需要大于0"
            if size > 10000:
                err = "size不能大于10000"
        except:
            err = "请输入正确的size，整数类型"
        if err:
            self.consumer_fetch_msg_body.value = err
            e.page.update()
            return

        self.consumer_fetch_msg_button.disabled = True
        self.consumer_fetch_msg_body.value = "fetching..."
        e.page.update()

        print(topic, group, size)

        st = time.time()
        res = "拉取成功"
        msgs = "拉取失败"

        try:
            msgs = kafka_service.fetch_msgs(topic=topic, group_id=group, size=size,
                                            timeout=self.kafka_fetch_timeout)
        except Exception as e_:
            traceback.print_exc()
            res = f"拉取失败：{e_}"
        self.consumer_fetch_msg_body.value = msgs

        et = time.time() - st
        res += f"\n拉取耗时{et} s"
        print(res)
        self.consumer_fetch_msg_button.disabled = False
        open_snack_bar(e.page, e.page.snack_bar, res)
