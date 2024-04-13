#!/usr/bin/env python
# -*-coding:utf-8 -*-
from views.broker import broker_instance
from views.monitor import monitor_instance
from views.settings import settings_instance
from views.simulate import simulate_instance
from views.suggest import suggest_instance
from views.topic import topic_instance

# 侧边栏的id -> 页面组件的映射
views_index_map = {
    0: broker_instance,
    1: topic_instance,
    2: simulate_instance,
    3: monitor_instance,
    4: settings_instance,
    5: suggest_instance,
}