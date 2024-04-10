#!/usr/bin/env python
# -*-coding:utf-8 -*-
import datetime
import time

from flet_core import Column, Row, TextStyle
import flet as ft

from service.common import dd_common_configs, S_Button
from service.kafka_service import kafka_service


class Monitor(object):
    """
    monitor页的组件
    """

    def __init__(self):
        self.key = "_monitor_topic_lag"
        self.topic_input = ft.TextField(
            label="支持通配符匹配，例如 *topicA*",
            label_style=TextStyle(size=12),
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
        self.data_1 = []
        self.labels = []
        self.left_axis = ft.ChartAxis(
            labels=[],
            labels_size=40,
        )
        self.chart = ft.LineChart(
            data_series=self.data_1,
            border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=1000, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            left_axis=self.left_axis,
            bottom_axis=ft.ChartAxis(
                labels=self.labels,
                labels_size=32,
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            min_y=0,
            max_y=0,
            min_x=0,
            max_x=10,
            expand=True,
        )

        self.controls = [
            Column(
                [
                    Row(
                        [
                            ft.Text("输入要监测的topic: "),
                            self.topic_input,
                            self.topic_groups_dd,
                            self.save_button

                        ]
                    ),
                ],
            ),
            self.chart

        ]

    def init(self, page: ft.Page = None):

        self.topic_groups_dd.options = [ft.dropdown.Option(text=i) for i in kafka_service.get_groups()]
        page.update()

        if not page.client_storage.contains_key(self.key):
            page.client_storage.set(self.key, [])

        while True:
            self.update(page)
            time.sleep(10)
            page.update()

    def click_save_config(self):
        pass

    def update(self, page: ft.Page):
        # _monitor_topic_lag: [ {time: { topic1: lag, topic2: lag} }, {} ]

        if self.topic_input.value is None or self.topic_groups_dd.value is None:
            return

        _lags = []
        topics = self.topic_input.value.split(',')
        group_id = self.topic_groups_dd.value
        topic_lag = kafka_service.get_topic_offsets(topics, group_id)
        dt = datetime.datetime.now().strftime("%m/%d %H:%M")

        lags: list = page.client_storage.get(self.key)
        if len(lags) >= 10:
            lags.pop(0)

        lags.append({dt: topic_lag})

        self.data_1.clear()
        self.labels.clear()

        for topic, lag in topic_lag.items():
            data_points = []
            for i, v in enumerate(lags):
                _lag = list(v.values())[0][topic]
                _lags.append(_lag)
                data_points.append(ft.LineChartDataPoint(i, _lag))
                self.labels.append(
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Container(
                            ft.Text(
                                list(v.keys())[0],
                                size=16,
                            ),
                            margin=ft.margin.only(top=10),
                        ),
                    )
                )
            self.data_1.append(
                ft.LineChartData(
                    data_points=data_points,
                    stroke_width=2,  # 线条宽度
                    color=ft.colors.CYAN,
                    curved=True,  # 曲线
                    stroke_cap_round=True,  # 绘制圆角线帽
                )
            )

        self.chart.max_y = max(_lags) * 1.2
        self.chart.horizontal_grid_lines.interval = max(_lags) * 1.2 / 15

