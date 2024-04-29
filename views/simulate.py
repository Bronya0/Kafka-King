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

from service.common import dd_common_configs, S_Button, open_snack_bar, KAFKA_KING_GROUP
from service.kafka_service import kafka_service


class Simulate(object):

    def __init__(self):
        self.producer_slider_value = None
        self.describe_topics_map = None
        self.describe_topics = None
        self.kafka_fetch_timeout = 10

        # if not kafka_service.kac:
        #     raise Exception("请先选择一个可用的kafka连接！")

        # producer tab's topic Dropdown
        self.producer_topic_dd = ft.Dropdown(
            label="请选择主题(必填)",
            # on_change=self.click_partition_topic_dd_onchange,
            **dd_common_configs
        )
        input_kwargs = {
            "width": 200,
            "height": 38,
            "text_size": 14,
            "content_padding": 10
        }

        # msg key
        self.producer_msg_key_input = ft.TextField(
            label="key",
            **input_kwargs
        )
        self.producer_acks_input = ft.TextField(
            label="acks：0、1、-1",
            value="1",
            **input_kwargs
        )

        self.producer_batch_size_input = ft.TextField(
            label="batch_size",
            value="16384",
            **input_kwargs

        )
        self.producer_linger_ms_input = ft.TextField(
            label="linger_ms",
            value="0",
            **input_kwargs
        )

        # 消息输入框
        self.producer_send_input = ft.TextField(
            multiline=True,
            keyboard_type=ft.KeyboardType.MULTILINE,
            max_length=10000,
            min_lines=8,
            max_lines=8,
            text_size=14,
            width=1000,
            hint_text="支持字符串，可以输入String、Json等消息。",
            adaptive=True
        )

        # 消息倍数
        self.producer_slider = ft.Slider(min=1, max=10000, divisions=50, label="×{value}", value=1,
                                         on_change=self.update_text, adaptive=True, width=1000)

        # send button
        self.producer_send_button = S_Button(
            text="发送消息",
            on_click=self.click_send_msg,
        )

        # producer tab's enable compress switch
        self.producer_compress_switch = ft.Switch(label="开启gzip压缩：", label_position=ft.LabelPosition.LEFT,
                                                  value=False)

        # producer tap
        self.producer_tab = ft.Tab(
            icon=ft.icons.TRENDING_UP, text="生产者", content=ft.Container()
        )

        # consumer tab's topic Dropdown
        self.consumer_topic_dd = ft.Dropdown(
            label="选择一个主题",
            **dd_common_configs
        )

        # consumer fetch size
        self.consumer_fetch_size_input = ft.TextField(
            label="拉取的消息数量",
            value="10",
            keyboard_type=ft.KeyboardType.NUMBER,
            **input_kwargs
        )

        # consumer fetch msg button
        self.consumer_fetch_msg_button = S_Button(
            text="拉取消息",
            on_click=self.click_fetch_msg,
        )

        # consumer fetch msg text
        self.consumer_fetch_msg_body = ft.Text(
            selectable=True,
        )

        # consumer tap
        self.consumer_tab = ft.Tab(
            icon=ft.icons.TOLL, text="消费者", content=ft.Container()
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

    def init(self, page=None):
        if not kafka_service.kac:
            return "请先选择一个可用的kafka连接！\nPlease select an available kafka connection first!"

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

        self.producer_slider_value = ft.Text(f"消息发送倍数：{self.producer_slider.value} (默认*1)")

        # init producer tab
        self.producer_tab.content = ft.Row(
            wrap=False,  # 禁止换行，以确保内容在一行内展示并出现滚动条
            scroll=ft.ScrollMode.ALWAYS,  # 设置滚动条始终显示
            expand=True,  # 让Row填充页面宽度
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                self.producer_topic_dd,
                                self.producer_msg_key_input,
                                self.producer_acks_input,
                                self.producer_batch_size_input,
                                self.producer_linger_ms_input
                            ]),
                            ft.Markdown(value="""# 输入单条消息内容"""),
                            # msg input
                            self.producer_send_input,
                            # enable gzip
                            self.producer_compress_switch,
                            # msg multiplier
                            self.producer_slider_value,
                            self.producer_slider,
                            # msg send button
                            self.producer_send_button
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                        adaptive=True
                    ),
                    alignment=ft.alignment.top_left,
                    padding=10,
                    adaptive=True
                )])

        # init consumer tab
        self.consumer_tab.content = ft.Row(
            wrap=False,  # 禁止换行，以确保内容在一行内展示并出现滚动条
            scroll=ft.ScrollMode.ALWAYS,  # 设置滚动条始终显示
            expand=True,  # 让Row填充页面宽度
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            self.consumer_topic_dd,
                            self.consumer_fetch_size_input,
                            ft.Text(f"内置消费者组（避免干扰正常业务）:  {KAFKA_KING_GROUP}"),
                            ft.Text(f"拉取超时时间:  {self.kafka_fetch_timeout}")
                        ]),
                        ft.Row([
                            self.consumer_fetch_msg_button,
                            S_Button(
                                text="清空界面",
                                on_click=self.clean_msg,
                            ),
                        ]),

                        self.consumer_fetch_msg_body,
                    ],

                        scroll=ft.ScrollMode.ALWAYS,
                    ),
                    alignment=ft.alignment.top_left, padding=10, adaptive=True
                )])

    def clean_msg(self, e):
        self.consumer_fetch_msg_body.value = None
        e.page.update()

    def click_send_msg(self, e: ControlEvent):
        """
        发送消息
        乘以倍数，and 是否压缩
        """
        try:
            topic = self.producer_topic_dd.value
            msg = self.producer_send_input.value
            enable_gzip = self.producer_compress_switch.value
            msg_multiplier = int(self.producer_slider.value)
            msg_key = self.producer_msg_key_input.value.rstrip()
            acks = int(self.producer_acks_input.value.rstrip())
            batch_size = int(self.producer_batch_size_input.value.rstrip())
            linger_ms = int(self.producer_linger_ms_input.value.rstrip())

            if acks not in [0, 1, -1] or linger_ms < 0 or batch_size < 0 or msg == "" or topic is None:
                raise Exception("参数填写不正确")
        except:
            open_snack_bar(e.page, "参数漏填、漏选或填写不正确")
            return

        ori = self.producer_send_button.text
        self.producer_send_button.text = "发送中..."
        self.producer_send_button.disabled = True
        e.page.update()

        st = time.time()
        res = "发送成功"
        success = True
        try:
            kafka_service.send_msgs(
                topic=topic,
                msg=msg.encode('utf-8'),
                enable_gzip=enable_gzip,
                msg_multiplier=msg_multiplier,
                msg_key=msg_key.encode('utf-8'),
                acks=acks,
                batch_size=batch_size,
                linger_ms=linger_ms
            )
        except Exception as e_:
            traceback.print_exc()
            res = "发送失败：{}".format(e_)
            success = False
        et = time.time() - st
        res += "\n发送耗时{} s".format(et)
        self.producer_send_button.text = ori
        self.producer_send_button.disabled = False
        open_snack_bar(e.page, res, success=success)

    def click_fetch_msg(self, e: ControlEvent):
        """
        根据topic 和 group、size、拉取消息
        """
        err = None
        topic = self.consumer_topic_dd.value
        if topic is None:
            err = "请选择topic"
        group = KAFKA_KING_GROUP
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
        self.consumer_fetch_msg_body.value = "拉取中，请稍后...\n将从上次拉取位置继续拉取，如无新消息可拉取，则会在10秒后超时返回\n拉取完成将显示在当前页面"
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
            res = "拉取失败：{}".format(e_)
        self.consumer_fetch_msg_body.value = msgs
        et = time.time() - st
        res += "\n拉取耗时{} s".format(et)
        print(res)
        self.consumer_fetch_msg_button.disabled = False
        open_snack_bar(e.page, res)

    def update_text(self, e):
        self.producer_slider_value.value = f"消息发送倍数：{int(e.control.value)} (默认*1)"
        e.page.update()
