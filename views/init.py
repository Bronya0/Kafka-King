#!/usr/bin/env python
# -*-coding:utf-8 -*-
from views.broker import Broker
from views.monitor import Monitor
from views.settings import Settings
from views.simulate import Simulate
from views.suggest import Suggest
from views.topic import Topic

# 侧边栏的id -> 页面组件的映射
views_index_map = {
    0: Broker(),
    1: Topic(),
    2: Simulate(),
    3: Monitor(),
    4: Settings(),
    5: Suggest(),
}