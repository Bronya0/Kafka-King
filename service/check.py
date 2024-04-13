#!/usr/bin/env python
# -*-coding:utf-8 -*-
import os

import flet as ft
import requests

from service.common import UPDATE_URL, BASEDIR, GITHUB_URL, close_dlg


def version_check(page: ft.Page):
    print("开始检查版本……", UPDATE_URL)

    res = requests.get(UPDATE_URL)
    if res.status_code != 200:
        res = requests.get(UPDATE_URL)
        if res.status_code != 200:
            res = requests.get(UPDATE_URL)
            if res.status_code != 200:
                return
    latest_version = res.json()['tag_name']
    body = res.json()['body']
    version = open(f'{BASEDIR}/assets/version.txt', 'r', encoding='utf-8').read().rstrip().replace('\n', '')
    if version != latest_version:
        print("需要更新 {} -> {}".format(version, latest_version))

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("🎉🎉发现新版本: {}".format(latest_version)),
            actions=[
                ft.Column(
                    [
                        ft.Column(
                            [
                                ft.Text(f"当前版本：{version}"),
                                ft.Text(body),
                            ],
                            scroll=ft.ScrollMode.ALWAYS,
                            height=160,
                        ),
                        ft.Row(
                            [
                                ft.TextButton(text="前往下载", url=GITHUB_URL),
                                ft.TextButton(text="下次再说", on_click=close_dlg, style=ft.ButtonStyle(color=ft.colors.GREY)),
                            ]
                        )
                    ],
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=8),
            open=True,
        )

        page.update()