#!/usr/bin/env python
# -*-coding:utf-8 -*-
import datetime

import flet as ft
import requests

from service.common import S_Button, GITHUB_URL, ISSUES_URL, ISSUES_API_URL, GITHUB_REPOS_URL


class Suggest(object):
    """
    Suggest
    """

    def __init__(self):
        self.issues = ft.Column(controls=[])
        self.repo = ft.Text(value="loading", size=16)

        self.controls = [
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(value="感谢使用", size=24),
                        ]
                    ),
                    self.repo,

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
                ],


            ),
            ft.Text("GITHUB ISSUES", size=20),
            self.issues,
            ft.Row([
                S_Button(text="软件主页",
                         url=GITHUB_URL,
                         ),
                S_Button(text="BUG反馈",
                         url=ISSUES_URL,
                         )
            ]),
        ]

    def init(self, page=None):
        api_res = requests.get(ISSUES_API_URL, timeout=60).json()
        api_repo_res = requests.get(GITHUB_REPOS_URL, timeout=60).json()
        self.repo.value = f"star: {api_repo_res['stargazers_count']}     forks: {api_repo_res['forks_count']}     language: {api_repo_res['language']} "
        page.update()

        n = 0
        controls = []
        for i in api_res:
            n += 1
            if n > 20:
                break
            time_str = datetime.datetime.fromisoformat(i['created_at'].replace("Z", "+00:00")).strftime("%Y-%m-%d")
            controls.append(
                ft.Row(
                    [
                        ft.Markdown(
                            value=f"""- {i['title']} {time_str} [详情]({i['html_url']})""",
                            selectable=True,
                            auto_follow_links=True,

                        ),
                    ]
                )
            )
        self.issues.controls = controls



