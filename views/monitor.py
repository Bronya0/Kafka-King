#!/usr/bin/env python
# -*-coding:utf-8 -*-
from flet_core import Column, Row, Text


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
                            Text("敬请期待")

                        ]
                    )
                ],
            )
        ]

    def init(self):
        pass
