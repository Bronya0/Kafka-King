#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/5 19:25
@File    : common.py
@Project : kafka-king
@Desc    : 
"""
import os

import flet
from flet_core import TextStyle

# 假设有一个全局的存储连接信息的变量
prefix = "__kafka_connects__"
GITHUB_URL = "https://github.com/Bronya0/Kafka-King"
UPDATE_URL = "https://api.github.com/repos/Bronya0/Kafka-King/releases/latest"
basedir = os.path.dirname(os.path.dirname(__file__))

c_version = open(f'{basedir}/assets/version.txt', 'r', encoding='utf-8').read().rstrip().replace('\n', '')
TITLE = "Kafka King {}".format(c_version)
CURRENT_KAFKA_CONNECT_KEY = "current_kafka_connect"


def S_Text(value, **kwargs):
    return flet.Text(
        selectable=True,
        value=value,
        tooltip=value,
        **kwargs
    )


def S_Button(**kwargs):
    return flet.ElevatedButton(
        style=flet.ButtonStyle(
            shape={
                flet.MaterialState.HOVERED: flet.RoundedRectangleBorder(radius=2),
                flet.MaterialState.DEFAULT: flet.RoundedRectangleBorder(radius=10),
            },
        ),
        **kwargs,
    )


def open_snack_bar(page, msg, success=False):
    page.snack_bar.content = flet.Text(msg)
    page.snack_bar.open = True
    if success:
        color = "#1677ff"
    else:
        color = "#000000"
    page.snack_bar.bgcolor = color
    page.update()


def close_dlg(e):
    e.page.dialog.open = False
    e.page.update()


dd_common_configs = {
    "options": [],
    "height": 36,
    "width": 200,
    "text_size": 14,
    "alignment": flet.alignment.center_left,
    "dense": True,
    "content_padding": 5,
    "bgcolor": '#F0F4FA',
}

input_kwargs = {
    "width": 200,
    "height": 35,
    "text_size": 16,
    "label_style": TextStyle(size=12),
    "content_padding": 10
}
