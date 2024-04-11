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
                            ft.Text(value="Thanks for using it~", size=24),
                        ]
                    ),

                    ft.Row(
                        [
                            ft.Markdown(
                                value="""
- suggest us on github: [{})
- If you like it, you can give it a star
                                """.format(GITHUB_URL),
                                selectable=True,
                                auto_follow_links=True,
                            ),
                        ]
                    ),
                    ft.Row([
                        S_Button(text="Update Kafka-king", icon=ft.icons.UPGRADE,
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
