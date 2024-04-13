#!/usr/bin/env python
# -*-coding:utf-8 -*-
import flet as ft

from service.common import S_Button, GITHUB_URL


class Suggest(object):
    """
    Suggest
    """

    def __init__(self):
        self.controls = [
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.FAVORITE, color='red'),
                            ft.Text(value="感谢使用~", size=24),
                        ]
                    ),

                    ft.Row(
                        [
                            ft.Markdown(
                                value="""
- 提建议: {}
- 喜欢的话可以给个star，更新更有动力！
                                """.format(GITHUB_URL),
                                selectable=True,
                                auto_follow_links=True,
                            ),
                        ]
                    ),
                    ft.Row([
                        S_Button(text="更新地址", icon=ft.icons.UPGRADE,
                                 url=GITHUB_URL,
                                 bgcolor="#F7E7E6",
                                 color="#DA3A66",
                                 )
                    ]),


                ],


            )
        ]

    def init(self, page=None):
        pass


suggest_instance = Suggest()