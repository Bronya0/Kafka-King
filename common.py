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

# 假设有一个全局的存储连接信息的变量
prefix = "__kafka_connects__"
GITHUB_URL = "https://github.com/Bronya0/Kafka-King"
UPDATE_URL = "https://api.github.com/repos/Bronya0/Kafka-King/releases/latest"
basedir = os.path.dirname(__file__)

c_version = open(f'{basedir}/assets/version.txt', 'r', encoding='utf-8').read().rstrip().replace('\n', '')
TITLE = "Kafka King {}".format(c_version)


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


def open_snack_bar(page, msg):
    page.snack_bar.content = flet.Text(msg)
    page.snack_bar.open = True
    page.update()


def close_dlg(e):
    e.page.dialog.open = False
    e.page.update()


dd_common_configs = {
    "options": [],
    "height": 30,
    "width": 200,
    "text_size": 14,
    "alignment": flet.alignment.center_left,
    "dense": True,
    "content_padding": 5,
    "bgcolor": '#F0F4FA',
}

