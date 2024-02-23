#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/23 18:04
@File    : setup.py.py
@Project : Kafka-King
@Desc    : 
"""
import os
from distutils.core import setup
from Cython.Build import cythonize

cur_path = os.path.dirname(os.path.abspath(__file__))
print(f'编译{cur_path}以下py文件')

# 执行python3 setup.py build_ext --inplace
setup(
    ext_modules=cythonize([os.path.join(dp, f) for dp, dn, filenames in os.walk(cur_path) for f in filenames if f.endswith('.py')], language_level="3")
)
