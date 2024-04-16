#!/usr/bin/env python
# -*-coding:utf-8 -*-
from views.broker import Broker
from views.monitor import Monitor
from views.settings import Settings
from views.simulate import Simulate
from views.suggest import Suggest
from views.topic import Topic


def get_view_instance(selected_index):
    """
    切连接的时候，返回重新new的对象，否则只返回单例对象
    """
    return {
        0: Broker(),
        1: Topic(),
        2: Simulate(),
        3: Monitor(),
        4: Settings(),
        5: Suggest(),
    }[selected_index]