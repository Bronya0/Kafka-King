#!/usr/bin/env python
# -*-coding:utf-8 -*-
import flet as ft

from common import S_Text


class Broker(object):
    """
    Cluster页的组件
    kafka版本、操作系统、集群信息等等
    """
    throttle_time_ms = 'throttle_time_ms'
    cluster_id = 'cluster_id'
    controller_id = 'controller_id'
    version = 'api_version'

    def __init__(self, ks):
        self.base_info = None
        self.api_version = None
        self.meta = None
        self.cluster_table = None
        self.KafkaService = ks

        if not self.KafkaService.kac:
            raise Exception("请先选择一个kafka连接！")

        # 先加载框架
        self.base_info_tab = ft.Tab(
            text="基础信息", content=ft.Container()
        )

        self.node_tab = ft.Tab(
            text='集群节点列表', content=ft.Container()
        )

        self.tab = ft.Tabs(
            animation_duration=300,
            tabs=[
                self.base_info_tab,
                self.node_tab
            ],
            expand=1,
        )

        self.controls = [
            self.tab
        ]

    def init(self):
        if not self.KafkaService.kac:
            return "请先选择一个kafka连接！"
        self.meta, self.api_version = self.KafkaService.get_brokers()
        self.base_info = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text(f"{self.throttle_time_ms}")),
                ft.DataColumn(S_Text(f"{self.cluster_id}")),
                ft.DataColumn(S_Text(f"{self.controller_id}")),
                ft.DataColumn(S_Text(f"{self.version}")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(S_Text(f"{self.meta[self.throttle_time_ms]}")),
                        ft.DataCell(S_Text(f"{self.meta[self.cluster_id]}")),
                        ft.DataCell(S_Text(f"{self.meta[self.controller_id]}")),
                        ft.DataCell(S_Text(f"{self.api_version}")),
                    ],
                )
            ],
            border=ft.border.all(1),
            border_radius=1,
            vertical_lines=ft.border.BorderSide(1),
            horizontal_lines=ft.border.BorderSide(1),

        )

        self.cluster_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("broker.id")),
                ft.DataColumn(S_Text("host")),
                ft.DataColumn(S_Text("port")),
                ft.DataColumn(S_Text("机架感知")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(S_Text(broker['node_id'])),
                        ft.DataCell(S_Text(broker['host'])),
                        ft.DataCell(S_Text(broker['port'])),
                        ft.DataCell(S_Text(broker['rack'])),
                    ],
                )
                for broker in self.meta['brokers']
            ],
            border=ft.border.all(1),
            border_radius=1,
            vertical_lines=ft.border.BorderSide(1),
            horizontal_lines=ft.border.BorderSide(1),

        )

        self.base_info_tab.content = ft.Container(
            content=self.base_info, alignment=ft.alignment.top_left, padding=10
        )

        self.node_tab.content = ft.Container(
            self.cluster_table, alignment=ft.alignment.top_left, padding=10
        )


