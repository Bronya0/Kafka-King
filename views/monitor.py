#!/usr/bin/env python
# -*-coding:utf-8 -*-
import random
import traceback

import flet as ft
from flet_core import Column, Row, TextStyle

from service.check import fetch_lag
from service.common import S_Button, open_snack_bar
from service.kafka_service import kafka_service


class Monitor(object):
    """
    monitor页的组件
    """

    def __init__(self):
        self.page = None
        self.key = "__monitor_topic_lag__"
        self.topic_input_key = "__monitor_topic_input_"
        self.topic_groups_key = "__monitor_topic_groups_"
        self.colors = [ft.colors.RED, ft.colors.ORANGE, ft.colors.YELLOW_900, ft.colors.BLUE, ft.colors.PURPLE,
                       ft.colors.GREEN, ft.colors.PINK]
        self.topic_input = ft.TextField(
            label="输入多个，英文逗号分隔",
            label_style=TextStyle(size=14),
            hint_text="topic1,topic2",
            width=400,
            height=30,
            text_size=14,
            content_padding=1
        )
        self.topic_groups_dd = ft.Dropdown(
            label="请选择消费组",
            label_style=TextStyle(size=14),
            width=200,
            height=30,
            dense=True,
            text_size=14,
            content_padding=1
        )
        self.save_button = S_Button(
            text="保存",
            height=38,
            on_click=self.click_save_config,
        )
        self.refresh_button = S_Button(
            text="更新",
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
                title=ft.Text("积压指标"),
                title_size=20,
                labels=[],
                labels_size=25,
            ),
            tooltip_bgcolor=ft.colors.WHITE,
            min_y=0,
            max_y=0,
            min_x=0,
            max_x=20,
            height=250,
            width=500,
        )

        # 生产
        self.produce_chart = ft.LineChart(
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
                title=ft.Text("消息生成速度"),
                title_size=20,
                labels=[],
                labels_size=25,
            ),
            tooltip_bgcolor=ft.colors.WHITE,
            min_y=0,
            max_y=0,
            min_x=0,
            max_x=20,
            height=250,
            width=500,
        )

        # 消费
        self.consumer_chart = ft.LineChart(
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
                title=ft.Text("消息消费速度"),
                title_size=20,
                labels=[],
                labels_size=25,
            ),
            tooltip_bgcolor=ft.colors.WHITE,
            min_y=0,
            max_y=0,
            min_x=0,
            max_x=20,
            height=250,
            width=500,
        )
        self.view = Column(
            [
                Row(
                    [
                        ft.Text("输入要监测的topic: "),
                        self.topic_input,
                        self.topic_groups_dd,
                        self.save_button,
                        self.refresh_button,
                        # self.alert_button

                    ]
                ),
                Row([
                    self.produce_chart,
                    self.consumer_chart,
                ], spacing=0),
                Row([
                    self.lag_chart,
                ]),
                # ft.Text(
                #     "横坐标：抓取时刻，纵坐标：消息积压指标；\n注意：每5分钟抓取一次，可以点刷新按钮手动抓取；离开当前tab页面不影响后台抓取；"
                #     "只保留20次数据；修改配置将清空历史数据"),

            ],
            scroll=ft.ScrollMode.ALWAYS,
            width=1100
        )
        self.lag_tab = ft.Tab(
            text='消息积压指标', content=ft.Row(
                wrap=False,  # 禁止换行，以确保内容在一行内展示并出现滚动条
                scroll=ft.ScrollMode.ALWAYS,  # 设置滚动条始终显示
                expand=True,  # 让Row填充页面宽度
                controls=[
                    ft.Container(
                        content=self.view,
                        alignment=ft.alignment.top_left, padding=10, adaptive=True
                    )
                ]),
            icon=ft.icons.LINE_STYLE
        )

        self.tab = ft.Tabs(
            animation_duration=300,
            tabs=[
                self.lag_tab,
            ],
            expand=1,
        )

        self.controls = [
            self.tab
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

        current_kafka_connect = kafka_service.connect_name
        # 获取每个kafka连接对应的这块的存储的配置值
        self.topic_input.value = page.client_storage.get(self.topic_input_key + current_kafka_connect)
        self.topic_groups_dd.value = page.client_storage.get(self.topic_groups_key + current_kafka_connect)

        self.page.update()

        self.update(page, First=True)

        self.page.update()

    def click_save_config(self, e):
        """
        保存配置，同时必须清除历史数据，不然不好兼容
        """
        page: ft.Page = e.page
        topics = self.topic_input.value
        topic_groups_dd = self.topic_groups_dd.value

        # 持久化，并和连接关联起来；修改配置则覆盖历史数据
        current_kafka_connect = kafka_service.connect_name
        if topics is not None:
            topics = topics.rstrip().replace('，', ',')
            page.client_storage.set(self.topic_input_key + current_kafka_connect, topics)
        if topic_groups_dd is not None:
            page.client_storage.set(self.topic_groups_key + current_kafka_connect, topic_groups_dd)

        page.client_storage.set(self.key + current_kafka_connect, {})
        open_snack_bar(page, "保存成功", success=True)

    def refresh(self, e):
        print("开始刷新offset……")
        self.refresh_button.disabled = True
        self.refresh_button.text = "更新中……"
        self.page.update()
        try:
            fetch_lag(page=self.page, only_one=True)
            self.update(self.page, First=False)
        except:
            traceback.print_exc()
        self.refresh_button.disabled = False
        self.refresh_button.text = "更新"
        self.page.update()

    def update(self, page: ft.Page, First=False):
        """
        只刷新组件
        First指首次切到该页面
        """
        print("读取积压offset……")

        # 清理页面
        for chart in [self.produce_chart, self.consumer_chart, self.lag_chart]:
            chart.data_series.clear()
            chart.bottom_axis.labels.clear()

        lag_x, produce_x = [], []
        # lags: {topic: [[time1, lag], ]}
        current_kafka_connect = kafka_service.connect_name
        connect_data_key = self.key + current_kafka_connect
        # lags: {topic: [[time1, end_offset, commit, lag], ]}
        lags = page.client_storage.get(connect_data_key)
        if not lags:
            return
        # 为每个topic绘制一条曲线
        # topic: [topic_end_offsets, topic_last_committed]
        for topic, lag_obj in lags.items():

            data_points = []
            produce_data_points = []
            consumer_data_points = []
            _max_lag, _max_produce_and_consume_offset = [], []
            for index, time_lag_list in enumerate(lag_obj):
                time_lag_list: list
                timestamp = time_lag_list[0]
                topic_end_offsets = time_lag_list[1]
                topic_last_committed = time_lag_list[2]
                topic_lag = topic_end_offsets - topic_last_committed
                # 一个曲线上的一个点的坐标
                data_points.append(ft.LineChartDataPoint(x=index, y=topic_lag,
                                                         tooltip=f"{topic}：{topic_lag}",
                                                         tooltip_align=ft.TextAlign.LEFT,
                                                         tooltip_style=ft.TextStyle(size=12),
                                                         ))

                # 生产速度曲线，减去差值得到速率
                produce_speed = 0
                consume_speed = 0
                if index > 0:
                    produce_speed = topic_end_offsets - lag_obj[index - 1][1]
                    consume_speed = topic_last_committed - lag_obj[index - 1][2]

                produce_data_points.append(ft.LineChartDataPoint(x=index, y=produce_speed,
                                                                 tooltip=f"{topic}：{produce_speed}",
                                                                 tooltip_align=ft.TextAlign.LEFT,
                                                                 tooltip_style=ft.TextStyle(size=12),
                                                                 ))

                # 消费速度曲线
                consumer_data_points.append(ft.LineChartDataPoint(x=index, y=consume_speed,
                                                                  tooltip=f"{topic}：{consume_speed}",
                                                                  tooltip_align=ft.TextAlign.LEFT,
                                                                  tooltip_style=ft.TextStyle(size=12),
                                                                  ))

                # 为每个点添加横坐标
                self.lag_chart.bottom_axis.labels.append(
                    ft.ChartAxisLabel(value=index, label=ft.Text(timestamp, size=12, )))
                self.produce_chart.bottom_axis.labels.append(
                    ft.ChartAxisLabel(value=index, label=ft.Text(timestamp, size=12, )))
                self.consumer_chart.bottom_axis.labels.append(
                    ft.ChartAxisLabel(value=index, label=ft.Text(timestamp, size=12, )))

                _max_lag.append(topic_lag)
                _max_produce_and_consume_offset.extend([produce_speed, consume_speed])

            # 取每个topic最大的积压，作为纵坐标label
            lag_x.append(max(_max_lag))
            produce_x.append(max(_max_produce_and_consume_offset))

            # 把一条曲线加进曲线列表里
            self.lag_chart.data_series.append(
                ft.LineChartData(
                    data_points=data_points,
                    stroke_width=2,  # 线条宽度
                    color=random.choice(self.colors),
                    curved=False,  # 直线
                    stroke_cap_round=True,  # 绘制圆角线帽
                    prevent_curve_over_shooting=True,  # 避免曲线超出边界
                ))
            self.produce_chart.data_series.append(
                ft.LineChartData(
                    data_points=produce_data_points,
                    stroke_width=2,  # 线条宽度
                    color=random.choice(self.colors),
                    curved=False,  # 直线
                    stroke_cap_round=True,  # 绘制圆角线帽
                    prevent_curve_over_shooting=True,  # 避免曲线超出边界
                ))
            self.consumer_chart.data_series.append(
                ft.LineChartData(
                    data_points=consumer_data_points,
                    stroke_width=2,  # 线条宽度
                    color=random.choice(self.colors),
                    curved=False,  # 直线
                    stroke_cap_round=True,  # 绘制圆角线帽
                    prevent_curve_over_shooting=True,  # 避免曲线超出边界
                ))

        # 取每个topic最大的积压，作为纵坐标label
        if not lag_x:
            return
        lag_x = list(set(lag_x))
        produce_x = list(set(produce_x))
        lag_x.sort()
        produce_x.sort()

        self.lag_chart.max_y = max(lag_x[-1] * 1.2, 100)
        self.produce_chart.max_y = max(produce_x[-1] * 1.2, 100)
        self.consumer_chart.max_y = max(produce_x[-1] * 1.2, 100)

        self.lag_chart.horizontal_grid_lines.interval = max(lag_x[-1] * 1.2 / 15, 10)
        self.produce_chart.horizontal_grid_lines.interval = max(produce_x[-1] * 1.2 / 15, 10)
        self.consumer_chart.horizontal_grid_lines.interval = max(produce_x[-1] * 1.2 / 15, 10)

        page.update()
