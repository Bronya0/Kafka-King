#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/11 15:58
@File    : font.py
@Project : Kafka-King
@Desc    : 
"""
import platform

WINDOWS_OS = "windows"
LINUX_OS = "linux"
MACOS_OS = "macos"
OTHER_OS = "other"


def get_os_platform():
    """
    获取系统默认字体
    """
    system = platform.system()

    if system == "Windows":
        return WINDOWS_OS
    elif system == "Linux":
        return LINUX_OS
    elif system == "Darwin":
        return MACOS_OS
    else:
        return OTHER_OS


def get_default_font(os_platform):
    """
    获取默认字体
    """
    if os_platform == WINDOWS_OS:
        return "Microsoft YaHei"
    elif os_platform == LINUX_OS:
        return "Noto Sans CJK SC"
    elif os_platform == MACOS_OS:
        return "PingFang SC"
    else:
        return "Microsoft YaHei"


