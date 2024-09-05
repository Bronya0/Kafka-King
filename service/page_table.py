#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/11 10:42
@File    : page_table.py
@Desc    :
"""
import math

import flet as ft
from flet_core import ControlEvent


class PageTable(ft.DataTable):

    def __init__(self, page, data_lst, row_func, page_num=1, page_size=8, **kwargs):
        """
        使用方式：
        1、传入page、数据集、以及初始化好的临时数据集、表头、每行数据的生成函数
        2、再在组件放置的地方下面使用.page_controls来引入分页组件
        """

        super().__init__(**kwargs)
        self.page = page
        self.page_num = page_num
        self.page_size = page_size

        self.kwargs = kwargs

        self.data_lst = data_lst
        self.data_lst_tmp = []

        self.page_info = ft.Text(f"{self.page_num}/{math.ceil(len(self.data_lst) / self.page_size)}")
        self.page_size_info = ft.Text(f"每页{self.page_size}条")
        self.page_controls = None
        self.init_page_controls()

        self.row_func = row_func  # 行数据生成函数, i、offset，以及data_lst迭代的每个元素
        self.init_rows()

    def init_rows(self):
        """
        更新行数据
        """
        self.rows = []
        offset = (self.page_num - 1) * self.page_size
        self.data_lst_tmp = self.data_lst[offset:offset + self.page_size]
        for i, data in enumerate(self.data_lst_tmp):
            self.rows.append(self.row_func(i, offset, data))

    def init_page_controls(self):
        """
        初始化翻页组件
        """
        self.page_controls = ft.Row(
                    [
                        # 翻页图标和当前页显示
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_size=20,
                            on_click=self.page_prev,
                            tooltip="上一页",
                        ),
                        self.page_info,
                        ft.IconButton(
                            icon=ft.icons.ARROW_FORWARD,
                            icon_size=20,
                            on_click=self.page_next,
                            tooltip="下一页",
                        ),
                        self.page_size_info,
                        ft.Slider(min=5, max=55, divisions=50, round=1, value=self.page_size, label="{value}",
                                  on_change_end=self.page_size_change),

                    ]
                )

    def update_page_info(self):
        """
        更新翻页组件
        """
        self.page_info.value = f"{self.page_num}/{int(len(self.data_lst) / self.page_size) + 1}"
        self.page_size_info.value = f"每页{self.page_size}条"

    def page_prev(self, e: ControlEvent):

        # page
        if self.page_num == 1:
            return
        self.page_num -= 1

        self.init_rows()

        self.update_page_info()
        self.page.update()

    def page_next(self, e):
        # page
        # 最后一页则return
        if self.page_num * self.page_size >= len(self.data_lst):
            return
        self.page_num += 1

        self.init_rows()

        self.update_page_info()

        self.page.update()

    def page_size_change(self, e):
        # page
        self.page_size = int(e.control.value)
        self.page_num = 1

        self.init_rows()

        self.update_page_info()

        self.page.update()
