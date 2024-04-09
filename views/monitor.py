#!/usr/bin/env python
# -*-coding:utf-8 -*-
from flet_core import Column, Row, Text, TextStyle
import flet as ft

from common import input_kwargs, dd_common_configs, S_Button
from service.kafka_service import kafka_service


class Monitor(object):
    """
    monitor页的组件
    """

    def __init__(self):
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

        self.chart = ft.LineChart(
            data_series=[],
            border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=1,
                        label=ft.Text("10K", size=14, weight=ft.FontWeight.BOLD),
                    ),
                    ft.ChartAxisLabel(
                        value=3,
                        label=ft.Text("30K", size=14, weight=ft.FontWeight.BOLD),
                    ),
                    ft.ChartAxisLabel(
                        value=5,
                        label=ft.Text("50K", size=14, weight=ft.FontWeight.BOLD),
                    ),
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=2,
                        label=ft.Container(
                            ft.Text(
                                "MAR",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                            ),
                            margin=ft.margin.only(top=10),
                        ),
                    ),
                    ft.ChartAxisLabel(
                        value=5,
                        label=ft.Container(
                            ft.Text(
                                "JUN",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                            ),
                            margin=ft.margin.only(top=10),
                        ),
                    ),
                    ft.ChartAxisLabel(
                        value=8,
                        label=ft.Container(
                            ft.Text(
                                "SEP",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                            ),
                            margin=ft.margin.only(top=10),
                        ),
                    ),
                ],
                labels_size=32,
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            min_y=0,
            max_y=6,
            min_x=0,
            max_x=11,
            # animate=5000,
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
                    self.chart
                ],
            )
        ]

    def init(self):
        self.topic_groups_dd.options = [ft.dropdown.Option(text=i) for i in kafka_service.get_groups()]


    def click_save_config(self):
        pass
