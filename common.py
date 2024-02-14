#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/5 19:25
@File    : common.py
@Project : kafka-king
@Desc    : 
"""
import flet


def S_Text(value, **kwargs):
    return flet.Text(
        selectable=True,
        value=value,
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


def open_snack_bar(page, snack_bar, msg):
    snack_bar.content = flet.Text(msg)
    page.snack_bar.open = True
    page.update()


def close_dlg(dlg_modal, page):
    dlg_modal.open = False
    page.update()


dd_common_configs = {
    "options": [],
    "height": 30,
    "width": 200,
    "text_size": 14,
    "alignment": flet.alignment.center_left,
    "dense": True,
    "content_padding": 10,
    "bgcolor": '#F0F4FA',
}