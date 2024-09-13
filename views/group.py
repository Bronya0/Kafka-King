#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
from typing import Optional

import flet as ft
from flet_core import ControlEvent
from kafka.structs import GroupInformation, MemberInformation

from service.common import S_Text, progress_bar, common_page
from service.kafka_service import kafka_service
from service.page_table import PageTable


class Group(object):
    """
    Group页的组件
    """

    def __init__(self):
        # _lag_label: when select consumer groups, use it, that is 'loading...'
        self.describe_groups = []
        self.page = None
        self.pr = progress_bar
        self.group_table: Optional[PageTable] = None
        self.members_table: Optional[PageTable] = None

        # consumer groups Dropdown

        # group list tap
        self.group_tab = ft.Tab(
            icon=ft.icons.LIST_ALT_OUTLINED, text="消费者组列表", content=ft.Row()
        )
        self.members_tab = ft.Tab(
            icon=ft.icons.VERIFIED_USER, text="消费者成员列表", content=ft.Row()
        )
        # all in one
        self.tab = ft.Tabs(
            tabs=[
                self.group_tab,
                self.members_tab,
            ],
            animation_duration=300,
            expand=True,
        )

        self.controls = [
            self.tab,
        ]

    def init(self, page=None):
        if not kafka_service.kac:
            return "请先选择一个可用的kafka连接！\nPlease select an available kafka connection first!"

        # 消费组初始化
        groups = kafka_service.get_groups()
        self.describe_groups = kafka_service.describe_groups(groups)

        self.init_table()

    def init_table(self, page_num=1, page_size=8):

        def row_func(i, offset, describe_group):
            describe_group: GroupInformation
            members: MemberInformation = describe_group.members

            return ft.DataRow(
                cells=[
                    ft.DataCell(S_Text(offset + i + 1)),
                    ft.DataCell(S_Text(describe_group.group)),
                    ft.DataCell(S_Text(describe_group.state)),
                    ft.DataCell(S_Text(describe_group.protocol_type)),
                    ft.DataCell(S_Text(describe_group.protocol)),
                    ft.DataCell(ft.TextButton(text=str(len(members)), on_click=self.click_member_button, data=describe_group.group)),

                ],
            )

        # init topic table data
        self.group_table = PageTable(
            page=common_page.page,
            page_num=page_num,
            page_size=page_size,
            data_lst=self.describe_groups,
            row_func=row_func,
            columns=[
                ft.DataColumn(S_Text("编号")),
                ft.DataColumn(S_Text("消费者组名")),
                ft.DataColumn(S_Text("状态")),
                ft.DataColumn(S_Text("协议类型")),
                ft.DataColumn(S_Text("协议")),
                ft.DataColumn(S_Text("消费者成员集合")),
            ],
            column_spacing=20,
            expand=True
        )

        self.group_tab.content = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,  # 设置滚动条始终显示
            controls=[
                ft.Container(
                    ft.Column(
                        [
                            ft.Row([self.group_table]),
                            self.group_table.page_controls
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                    ), alignment=ft.alignment.top_left, padding=10)
            ],
        )

    def create_members_table(self, group_name, page, page_num=1, page_size=8):

        def row_func(i, offset, member):
            return ft.DataRow(
                cells=[
                    ft.DataCell(S_Text(member.member_id, length=20)),
                    ft.DataCell(S_Text(member.client_id, length=20)),
                    ft.DataCell(S_Text(member.client_host)),
                    ft.DataCell(S_Text(json.dumps(member.member_metadata.subscription, ensure_ascii=False) if member.member_metadata.subscription else None)),
                    ft.DataCell(S_Text(json.dumps(member.member_assignment.assignment, ensure_ascii=False) if member.member_assignment.assignment else None)),

                ],
            )
        print(group_name)
        members_lst = []
        for g in self.describe_groups:
            if g.group == group_name:
                members_lst = g.members
                break
        print(members_lst)
        self.members_table = PageTable(
            page=page,
            page_num=page_num,
            page_size=page_size,
            data_lst=members_lst,
            row_func=row_func,
            columns=[
                ft.DataColumn(S_Text("消费者成员id")),
                ft.DataColumn(S_Text("客户端id")),
                ft.DataColumn(S_Text("host")),
                ft.DataColumn(S_Text("订阅topic")),
                ft.DataColumn(S_Text("分区分配")),
            ],
            column_spacing=20,
            expand=True
        )

        self.group_tab.content = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,  # 设置滚动条始终显示
            controls=[
                ft.Container(
                    ft.Column(
                        [
                            ft.Row([self.group_table]),
                            self.group_table.page_controls
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                    ), alignment=ft.alignment.top_left, padding=10)
            ],
        )
        self.members_tab.content = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,  # 设置滚动条始终显示
            controls=[
                ft.Container(
                    ft.Column(
                        [
                            S_Text(f"消费者组：{group_name}"),
                            ft.Row([
                                self.members_table
                            ]),
                            self.members_table.page_controls
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                    ), alignment=ft.alignment.top_left, padding=10)
            ],
        )

    def click_member_button(self, e: ControlEvent):
        """
        点击成员信息，跳转到成员tab
        """
        group_name_ = e.control.data
        self.tab.selected_index = 1
        self.create_members_table(group_name=group_name_, page=e.page)
        e.page.update()
