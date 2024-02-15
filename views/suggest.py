#!/usr/bin/env python
# -*-coding:utf-8 -*-
import flet as ft

from common import S_Button


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
- suggest us on github: [https://github.com/Bronya0/Kafka-King](https://github.com/Bronya0/Kafka-King)
- If you like it, you can give it a star
                                """,
                                selectable=True,
                                auto_follow_links=True,
                            ),
                        ]
                    ),
                    ft.Row([
                        S_Button(text="Update Kafka-king", icon=ft.icons.UPGRADE,
                                 url="https://github.com/Bronya0/Kafka-King",
                                 bgcolor="#F7E7E6",
                                 color="#DA3A66",
                                 )
                    ]),


                ],


            )
        ]

    def init(self):
        pass
