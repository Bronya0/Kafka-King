#!/usr/bin/env python
# -*-coding:utf-8 -*-
import flet as ft

from service.common import S_Text


class Help(object):
    """
    settings页的组件
    """

    def __init__(self):

        self.controls = [
            ft.Column(
                [
                    ft.Text("使用帮助", size=30),
                    S_Text("1、如何将程序固定到任务栏？右键exe -> 选择固定到任务栏，或者将exe直接拖动到任务栏都可，但是无法通过右键窗口固定（底层框架缺陷）"),
                    S_Text("2、程序启动不怎么快？Python的原因，不影响启动后的性能"),
                    S_Text("3、程序吃不吃内存？正常情况下差不多100M内存左右，比较少，如果topic数量很多，内存占用会增加（主要是渲染页面用，切换一下就回收了）"),
                    S_Text("4、遇到bug怎么办？点【建议】，到【BUG反馈】也就是github提issue，或者直接联系我。"),
                    S_Text("5、往期版本汇总：https://github.com/Bronya0/Kafka-King/releases"),
                    S_Text("6、有没有打算开发类似的redis、es工具？懒癌晚期，看有没有时间吧，可以群里踢我"),
                    S_Text("7、qq技术群：964440643，交流中间件或软件开发知识"),
                    ft.Image(src="qq.jpg", width=220)

                ],
            )
        ]

    def init(self, page=None):
        pass


