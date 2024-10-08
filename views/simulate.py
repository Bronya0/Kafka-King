#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/14 10:50
@File    : simulate.py
@Project : kafka-king
@Desc    : 
"""
import os
import time
import traceback

import flet as ft
from flet_core import ControlEvent

from service.common import dd_common_configs, S_Button, open_snack_bar, KAFKA_KING_GROUP, build_tab_container, \
    progress_bar, open_directory, CONFIG_KEY
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
            expand=True,
            hint_text="支持字符串，可以输入String、Json等消息。",
        )

        self.headers_input = ft.TextField(
            multiline=True,
            keyboard_type=ft.KeyboardType.MULTILINE,
            max_length=999,
            min_lines=1,
            max_lines=4,
            text_size=12,
            expand=True,
            hint_text="输入消息header，键值用英文冒号隔开，键值对之间用英文逗号隔开。例如：key1:value1,key2:value2，格式不正确会失败",
        )

        # 消息倍数
        self.producer_slider = ft.Slider(min=1, max=10000, divisions=50, label="×{value}", value=1,
                                         on_change=self.update_text, expand=True)

        # send button
        self.producer_send_button = S_Button(
            text="发送消息",
            on_click=self.click_send_msg,
        )

        # producer tab's enable compress switch
        self.producer_compress_switch = ft.Switch(label="gzip压缩：", label_position=ft.LabelPosition.LEFT,
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
            text="拉取消息并utf8解码",
            on_click=self.click_fetch_msg,
        )

        self.consumer_fetch_utf8_msg_button = S_Button(
            text="拉取消息utf8解码并保存到本地文件",
            on_click=self.click_fetch_utf8_msg_save,
        )
        self.consumer_fetch_msg_button_save = S_Button(
            text="拉取二进制消息并保存到本地文件",
            tooltip="有些消息没法utf-8解码，例如avro、protobuf、binlog等，可以下载自行解码",
            on_click=self.click_fetch_msg_save,
        )
        # consumer fetch msg text
        self.consumer_fetch_msg_body = ft.Text(
            selectable=True,
            expand=True
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
        self.producer_tab.content = build_tab_container(
            [
                ft.Row([
                    self.producer_topic_dd,
                    self.producer_msg_key_input,
                    self.producer_acks_input,
                    self.producer_batch_size_input,
                    self.producer_linger_ms_input
                ]),
                ft.Markdown(value="""## 输入单条消息内容"""),

                ft.Row(
                    [
                        # msg input
                        self.producer_send_input,
                    ]
                ),
                ft.Markdown(value="""### 输入消息Headers（可选）"""),
                ft.Row(
                    [
                        self.headers_input,
                    ]
                ),
                ft.Row(
                    [
                        # enable gzip
                        self.producer_compress_switch,
                    ]
                ),
                ft.Row(
                    [
                        # msg multiplier
                        self.producer_slider_value,
                    ]
                ),
                ft.Row(
                    [
                        self.producer_slider,
                    ]
                ),
                # msg send button
                self.producer_send_button
            ]
        )

        # init consumer tab
        self.consumer_tab.content = build_tab_container(
            [
                ft.Row([
                    self.consumer_topic_dd,
                    self.consumer_fetch_size_input,
                    ft.Text(f"内置消费者组（避免干扰正常业务）:  {KAFKA_KING_GROUP}"),
                    ft.Text(f"拉取超时时间:  {self.kafka_fetch_timeout}")
                ]),
                ft.Row([
                    self.consumer_fetch_msg_button,
                    self.consumer_fetch_utf8_msg_button,
                    self.consumer_fetch_msg_button_save,
                    S_Button(
                        text="清空界面",
                        on_click=self.clean_msg,
                    ),
                ]),
                ft.Row(
                    [
                        self.consumer_fetch_msg_body,
                    ]
                )

            ])

    def clean_msg(self, e):
        self.consumer_fetch_msg_body.value = None
        self.consumer_fetch_msg_button.disabled = False
        e.page.update()

    def click_send_msg(self, e: ControlEvent):
        """
        发送消息
        乘以倍数，and 是否压缩
        """
        try:

            topic = self.producer_topic_dd.value
            msg = self.producer_send_input.value
            headers = self.headers_input.value
            enable_gzip = self.producer_compress_switch.value
            msg_multiplier = int(self.producer_slider.value)
            msg_key = self.producer_msg_key_input.value.rstrip()
            acks = int(self.producer_acks_input.value.rstrip())
            batch_size = int(self.producer_batch_size_input.value.rstrip())
            linger_ms = int(self.producer_linger_ms_input.value.rstrip())

            if acks not in [0, 1, -1] or linger_ms < 0 or batch_size < 0 or msg == "" or topic is None:
                raise Exception("acks、linger_ms、batch_size、msg、topic参数填写不正确")
        except Exception as e_:
            open_snack_bar(e.page, f"参数漏填、漏选或填写不正确：{e_}")
            return
        try:
            headers_lst = None
            if headers:
                headers = headers.strip()
                headers_lst = [(i.split(":")[0], i.split(":")[1].encode("utf-8")) for i in headers.split(",")]
                print("headers_lst: ", headers_lst)
        except Exception as e_:
            open_snack_bar(e.page, f"headers填写不正确：{e_}")
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
                linger_ms=linger_ms,
                headers_lst=headers_lst,
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
        progress_bar.visible = True
        progress_bar.update()

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
            progress_bar.visible = False

            e.page.update()
            return

        self.consumer_fetch_msg_button.disabled = True
        e.page.update()

        print(topic, group, size)

        st = time.time()
        res = "拉取成功"
        msgs = "拉取失败"

        try:
            msgs, _ = kafka_service.fetch_msgs(topic=topic, group_id=group, size=size,
                                               timeout=self.kafka_fetch_timeout)
        except Exception as e_:
            traceback.print_exc()
            res = "拉取失败：{}".format(e_)
        _, topic_lag = kafka_service.get_topic_offsets(topics=[topic], group_id=None)
        self.consumer_fetch_msg_body.value = f"【末尾offset：{topic_lag.get(topic, ['', ''])[0]} || 当前offset：{topic_lag.get(topic, ['', ''])[1]}】\n\n{msgs}"
        e.page.update()

        et = time.time() - st
        res += "\n拉取耗时{} s".format(et)
        print(res)
        progress_bar.visible = False

        self.consumer_fetch_msg_button.disabled = False
        open_snack_bar(e.page, res)

    def click_fetch_utf8_msg_save(self, e: ControlEvent):
        """
        根据topic 和 group、size、拉取消息并保存
        """
        progress_bar.visible = True
        progress_bar.update()

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
            progress_bar.visible = False

            e.page.update()
            return

        self.consumer_fetch_utf8_msg_button.disabled = True
        e.page.update()

        print(topic, group, size)
        res = ""
        ori_msgs_lst = []
        try:
            msgs, ori_msgs_lst = kafka_service.fetch_msgs(topic=topic, group_id=group, size=size,
                                                          timeout=self.kafka_fetch_timeout)
        except Exception as e_:
            traceback.print_exc()
            res = "拉取失败：{}".format(e_)

        config = e.page.client_storage.get(CONFIG_KEY)
        root = config.get("export_dir") if config.get("export_dir") else "/kafka-king-export"
        if not os.path.exists(root):
            os.mkdir(root)

        path = os.path.join(root, f"{topic}_{group}_{size}_{int(time.time())}.txt")
        with open(path, 'w', encoding='utf-8') as f:
            for i in ori_msgs_lst:
                try:
                    v = i.decode('utf-8') if i is not None else ""
                except:
                    v = "无法解码"
                f.write(v)
                f.write('\n')

        bar = ft.SnackBar(content=ft.Text(f"成功导出：{path}", selectable=True), open=True, action="打开目录",
                          on_action=lambda e: open_directory(root))
        e.page.snack_bar = bar

        self.consumer_fetch_utf8_msg_button.disabled = False
        progress_bar.visible = False

        if res:
            self.consumer_fetch_msg_body.value = res

        e.page.update()

    def click_fetch_msg_save(self, e: ControlEvent):
        """
        根据topic 和 group、size、拉取消息并保存
        """
        progress_bar.visible = True
        progress_bar.update()

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
            progress_bar.visible = False

            e.page.update()
            return

        self.consumer_fetch_msg_button_save.disabled = True
        e.page.update()

        print(topic, group, size)
        res = ""
        ori_msgs_lst = []
        try:
            msgs, ori_msgs_lst = kafka_service.fetch_msgs(topic=topic, group_id=group, size=size,
                                                          timeout=self.kafka_fetch_timeout)
        except Exception as e_:
            traceback.print_exc()
            res = "拉取失败：{}".format(e_)

        config = e.page.client_storage.get(CONFIG_KEY)
        root = config.get("export_dir") if config.get("export_dir") else "/kafka-king-export"
        if not os.path.exists(root):
            os.mkdir(root)

        path = os.path.join(root, f"{topic}_{group}_{size}_{int(time.time())}.bin")
        with open(path, 'wb') as f:
            for i in ori_msgs_lst:
                f.write(i)
                f.write(b'\n')

        bar = ft.SnackBar(content=ft.Text(f"成功导出：{path}", selectable=True), open=True, action="打开目录",
                          on_action=lambda e: open_directory(root))
        e.page.snack_bar = bar

        self.consumer_fetch_msg_button_save.disabled = False
        progress_bar.visible = False

        if res:
            self.consumer_fetch_msg_body.value = res

        e.page.update()

    def update_text(self, e):
        self.producer_slider_value.value = f"消息发送倍数：{int(e.control.value)} (默认*1)"
        e.page.update()
