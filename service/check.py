#!/usr/bin/env python
# -*-coding:utf-8 -*-
import datetime
import time
import traceback

import flet as ft
import requests

from service.common import UPDATE_URL, BASEDIR, GITHUB_URL, close_dlg
from service.kafka_service import kafka_service


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
            modal=False,
            title=ft.Text("🎉🎉发现新版本: {}".format(latest_version)),
            actions=[
                ft.Row(
                    controls=[
                        ft.Column(
                            [
                                ft.Column(
                                    [
                                        ft.Text(f"当前版本：{version}"),
                                        ft.Text(body, selectable=True),
                                    ],
                                    scroll=ft.ScrollMode.ALWAYS,
                                    height=180,
                                    width=600
                                ),
                                ft.Row(
                                    [
                                        ft.TextButton(text="前往下载", url=GITHUB_URL),
                                        ft.TextButton(text="下次再说", on_click=close_dlg, tooltip="长期未更新可能会导致故障累积",
                                                      style=ft.ButtonStyle(color=ft.colors.GREY)),
                                    ]
                                )
                            ],
                            scroll=ft.ScrollMode.ALWAYS,
                        )],
                    scroll=ft.ScrollMode.ALWAYS,

                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=8),
            open=True,
        )

        page.update()


def fetch_lag(page: ft.Page, only_one=False):
    """
    后台线程定时抓取消息积压量，为了解耦，不刷新页面组件
    """
    key = "__monitor_topic_lag__"
    topic_input_key = "__monitor_topic_input_"
    topic_groups_key = "__monitor_topic_groups_"
    while True:
        print("获取当前连接对应的历史积压数据，并更新")
        current_kafka_connect = kafka_service.connect_name
        if current_kafka_connect is None:
            time.sleep(60 * 1)
            continue
        connect_data_key = key + current_kafka_connect
        # lags: {topic: [[time1, end_offset, commit, lag], ]}
        lags = page.client_storage.get(connect_data_key)
        if not lags:
            lags = {}
        topics = page.client_storage.get(topic_input_key + current_kafka_connect)
        group_id = page.client_storage.get(topic_groups_key + current_kafka_connect)
        print(f"存储的topics: {topics}, group: {group_id}")
        if topics is None or group_id is None:
            if only_one:
                return
            time.sleep(60 * 1)
            continue
        print("开始查询积压……")
        try:
            topics = topics.split(',')
            topic_offset, topic_lag = kafka_service.get_topic_offsets(topics, group_id)
        except Exception as e:
            traceback.print_exc()
            time.sleep(60 * 1)
            continue

        print(f"查询完毕，topic_lag： {topic_lag}")
        # 只保留指定数量的数据
        # topic: [topic_end_offsets, topic_last_committed]
        for i, v in topic_lag.items():
            lags.setdefault(i, [])
            if len(lags[i]) >= 20:
                lags[i].pop(0)
            lags[i].append(
                [datetime.datetime.now().strftime("%H:%M"), v[0], v[1]]
            )
        # 更新
        print("lags: ", lags)
        page.client_storage.set(connect_data_key, lags)

        if only_one:
            return
        time.sleep(60 * 5)
