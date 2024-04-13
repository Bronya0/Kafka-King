#!/usr/bin/env python
# -*-coding:utf-8 -*-
import datetime
import random
import time
import traceback

from flet_core import Column, Row, TextStyle
import flet as ft

from service.common import dd_common_configs, S_Button, CURRENT_KAFKA_CONNECT_KEY, open_snack_bar
from service.kafka_service import kafka_service


class Monitor(object):
    """
    monitor页的组件
    """

    def __init__(self):
        self.page = None
        self.key = "_monitor_topic_lag"
        self.connect_data_key = None
        self.topic_input_key = "_monitor_topic_input"
        self.topic_groups_key = "_monitor_topic_groups"
        self.current_kafka_connect = None
        self.topic_color_map = {}

        self.topic_input = ft.TextField(
            label="输入多个，英文逗号分隔",
            label_style=TextStyle(size=14),
            hint_text="topic1,topic2",
            width=300,
            height=35,
            text_size=14,
            content_padding=10
        )
        self.topic_groups_dd = ft.Dropdown(
            label="请选择消费组",
            **dd_common_configs
        )
        self.save_button = S_Button(
            text="保存",
            height=38,
            on_click=self.click_save_config,
        )
        self.refresh_button = S_Button(
            text="刷新",
            tooltip="刷新",
            height=38,
            on_click=self.refresh,
        )
        self.alert_button = S_Button(
            text="告警外发",
            tooltip="设置阈值，达到阈值后将告警信息外发到指定接口，例如企微、钉钉",
            height=38,
            on_click=self.refresh,
        )

        # 积压
        self.lag_chart = ft.LineChart(
            data_series=[],
            border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=1000, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            left_axis=ft.ChartAxis(
                labels=[],
                labels_size=100,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[],
                labels_size=20,
            ),
            tooltip_bgcolor=ft.colors.WHITE,
            min_y=0,
            max_y=0,
            min_x=0,
            max_x=19,
            height=500,
            width=1000,
        )
        self.controls = [
            Column(
                [
                    Row(
                        [
                            ft.Text("输入要监测的topic: "),
                            self.topic_input,
                            self.topic_groups_dd,
                            self.save_button,
                            self.refresh_button,
                            # self.alert_button

                        ], adaptive=True
                    ),
                    Row([
                        self.lag_chart,
                    ], adaptive=True),
                    ft.Text(
                        "注意：横坐标：抓取时刻，纵坐标：消息积压指标；每5分钟抓取一次，可以点刷新按钮手动抓取；离开当前tab页面不影响后台抓取；"
                        "\n只保留20次数据；修改配置将清空历史数据"),

                ],
                scroll=ft.ScrollMode.ALWAYS,
                height=1200,
                adaptive=True

            ),

        ]

    def init(self, page: ft.Page = None):
        if not kafka_service.kac:
            return "请先选择一个可用的kafka连接！\nPlease select an available kafka connection first!"
        self.page = page
        groups = kafka_service.get_groups()
        if groups:
            self.topic_groups_dd.options = [ft.dropdown.Option(text=i) for i in groups]

        else:
            self.topic_groups_dd.label = "无消费组"

        self.current_kafka_connect = page.client_storage.get(CURRENT_KAFKA_CONNECT_KEY)
        # 获取每个kafka连接对应的这块的存储的配置值
        self.topic_input.value = page.client_storage.get(self.topic_input_key + self.current_kafka_connect)
        self.topic_groups_dd.value = page.client_storage.get(self.topic_groups_key + self.current_kafka_connect)
        self.connect_data_key = self.key + self.current_kafka_connect

        self.page.update()

        self.update(page, First=True)

        self.page.update()

    def click_save_config(self, e):
        page: ft.Page = e.page
        topics = self.topic_input.value

        # 持久化，并和连接关联起来
        if topics is not None:
            topics = topics.rstrip().replace('，', ',')
            page.client_storage.set(self.topic_input_key + self.current_kafka_connect, topics)
        if self.topic_groups_dd.value is not None:
            page.client_storage.set(self.topic_groups_key + self.current_kafka_connect, self.topic_groups_dd.value)

        # 修改配置则清空历史数据
        page.client_storage.remove(self.connect_data_key)
        open_snack_bar(page, "保存成功", success=True)

    def refresh(self, e):
        self.refresh_button.disabled = True
        tooltip = self.refresh_button.tooltip
        self.refresh_button.tooltip = "刷新中……"
        e.page.update()
        try:
            self.update(e.page)
        except:
            traceback.print_exc()
        self.refresh_button.disabled = False
        self.refresh_button.tooltip = tooltip
        e.page.update()

    def fetch_lag(self, page: ft.Page):
        """
        后台线程定时抓取消息积压量
        """
        time.sleep(20)
        while True:
            self.update(page)
            time.sleep(60 * 5)

    def update(self, page: ft.Page, First=False):
        # _monitor_topic_lag: [ {time: { topic1: lag, topic2: lag} }, {} ]
        print("读取积压offset……")
        if self.topic_input.value is None or self.topic_groups_dd.value is None:
            print("配置不合要求")
            return
        lags = page.client_storage.get(self.connect_data_key)
        if not lags:
            lags = {}
        if not First or not lags:
            topics = self.topic_input.value.split(',')
            group_id = self.topic_groups_dd.value
            # lags: {topic: [[time1, end_offset, commit, lag], ]}

            topic_offset, topic_lag = kafka_service.get_topic_offsets(topics, group_id)
            dt = datetime.datetime.now().strftime("%H:%M")
            # 只保留指定数量的数据
            for i, v in topic_lag.items():
                lags.setdefault(i, [])
                if len(lags[i]) >= 20:
                    lags[i].pop(0)
                lags[i].append([dt, v])
            page.client_storage.set(self.connect_data_key, lags)

        self.lag_chart.data_series.clear()
        self.lag_chart.bottom_axis.labels.clear()
        colors = [ft.colors.RED, ft.colors.ORANGE, ft.colors.YELLOW_900, ft.colors.BLUE, ft.colors.PURPLE, ft.colors.GREEN, ft.colors.PINK]
        print(lags)
        x = []
        # lags: {topic: [[time1, lag], ]}

        # 为每个topic绘制一条曲线
        for topic, lag_obj in lags.items():

            data_points = []
            _max_lag = []
            for index, time_lag_list in enumerate(lag_obj):
                time_lag_list: list
                timestamp = time_lag_list[0]
                topic_lag = time_lag_list[1]
                # 一个曲线上的一个点的坐标
                data_points.append(ft.LineChartDataPoint(x=index, y=topic_lag,
                                                         tooltip=f"{topic}：{topic_lag}",
                                                         tooltip_align=ft.TextAlign.LEFT,
                                                         tooltip_style=ft.TextStyle(size=12),
                                                         ))

                if len(self.lag_chart.bottom_axis.labels) < len(lag_obj):
                    # 横坐标对应label
                    self.lag_chart.bottom_axis.labels.append(
                        ft.ChartAxisLabel(
                            value=index,
                            label=ft.Text(timestamp, size=12, ),
                        )
                    )
                _max_lag.append(topic_lag)

            # 取每个topic最大的积压，作为纵坐标label
            x.append(max(_max_lag))
            if topic in self.topic_color_map:
                line_color = self.topic_color_map[topic]
            else:
                line_color = random.choice(colors)
                self.topic_color_map[topic] = line_color

            # 把一条曲线加进曲线列表里
            self.lag_chart.data_series.append(
                ft.LineChartData(
                    data_points=data_points,
                    stroke_width=2,  # 线条宽度
                    color=line_color,
                    curved=True,  # 曲线
                    stroke_cap_round=True,  # 绘制圆角线帽

                )
            )

        # 取每个topic最大的积压，作为纵坐标label
        x = list(set(x))
        x.sort()

        self.lag_chart.max_y = x[-1] * 1.2
        self.lag_chart.horizontal_grid_lines.interval = x[-1] * 1.2 / 15


monitor_instance = Monitor()