#!/usr/bin/env python
# -*-coding:utf-8 -*-
import flet
from flet_core import Column, Row


class Monitor(object):
    """
    monitor页的组件
    """

    def __init__(self):
        self.controls = [
            Column(
                [
                    Row(
                        [
                            flet.Text("敬请期待")

                        ]
                    )
                ],
            )
        ]

    def init(self):
        pass
