#!/usr/bin/env python
# -*-coding:utf-8 -*-
import flet as ft
from flet_core import ControlEvent

from service.common import S_Button, open_snack_bar, PAGE_WIDTH, PAGE_HEIGHT, CONFIG_KEY, PAGE_MIN_WIDTH, \
    PAGE_MIN_HEIGHT
from service.translate import lang


class Settings(object):
    """
    settings页的组件
    """

    def __init__(self):

        # 链接下拉
        self.lang_dd = ft.Dropdown(
            options=[
                ft.dropdown.Option("简体中文"),
                ft.dropdown.Option("en")
            ],
            height=35,
            width=120,
            text_size=12,
            alignment=ft.alignment.center_left,
            content_padding=5,
        )

        self.save_button = S_Button(
            text="保存",
            on_click=self.click_save_msg,
        )

        self.width = ft.TextField(
            label='宽',
            width=120,
            height=35,
            text_size=14,
            content_padding=5
        )
        self.height = ft.TextField(
            label='高',
            width=120,
            height=35,
            text_size=14,
            content_padding=5
        )
        self.controls = [
            ft.Column(
                [
                    ft.Row(
                       [
                           ft.Text("语言："),
                           self.lang_dd,
                       ]
                    ),

                    ft.Row(
                        [
                            ft.Text("界面宽高："),
                            self.width,
                            self.height,
                            ft.Text(f"默认：{PAGE_WIDTH}x{PAGE_HEIGHT} 最小值：{PAGE_MIN_WIDTH}x{PAGE_MIN_HEIGHT}"),
                        ]
                    ),
                    self.save_button,

                ],
            )
        ]

    def init(self, page=None):
        config = page.client_storage.get(CONFIG_KEY)

        language = config.get("language")
        if language is not None:
            self.lang_dd.value = language
        else:
            self.lang_dd.value = "简体中文"

        self.width.value = config['default_width'] if 'default_width' in config else PAGE_WIDTH
        self.height.value = config['default_height'] if 'default_height' in config else PAGE_HEIGHT

    def click_save_msg(self, e: ControlEvent):
        language = self.lang_dd.value

        width = int(self.width.value) if self.width.value else PAGE_WIDTH
        height = int(self.height.value) if self.height.value else PAGE_HEIGHT

        if width < PAGE_MIN_WIDTH or height < PAGE_MIN_HEIGHT:
            open_snack_bar(e.page, "宽高不能小于最小值", success=False)
            return

        config = {
            "language": language,
            "default_width": width,
            "default_height": height,
        }
        e.page.client_storage.set(CONFIG_KEY, config)

        lang.language = language

        if width:
            e.page.window_width = width
        if height:
            e.page.window_height = height

        open_snack_bar(e.page, "保存成功", success=True)



