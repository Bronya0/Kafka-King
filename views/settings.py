#!/usr/bin/env python
# -*-coding:utf-8 -*-
import flet as ft
from flet_core import ControlEvent

from service.common import S_Button, open_snack_bar
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
            dense=True,
            content_padding=10,
            focused_bgcolor='#ff0000',
        )

        self.save_button = S_Button(
            text="保存",
            on_click=self.click_save_msg,
        )

        self.controls = [
            ft.Column(
                [
                    ft.Text("语言："),
                    self.lang_dd,
                    self.save_button,
                    ft.Row(
                        [
                        ]
                    )
                ],
            )
        ]

    def init(self, page=None):
        language = self.lang_dd.page.client_storage.get("language")
        if language is not None:
            self.lang_dd.value = language
        else:
            self.lang_dd.value = "简体中文"

    def click_save_msg(self, e: ControlEvent):
        language = self.lang_dd.value
        self.lang_dd.page.client_storage.set('language', language)
        lang.language = language
        open_snack_bar(e.page, "保存成功", success=True)
