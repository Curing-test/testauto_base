#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   main.py
@Version:   1.0
@Desc   :   None
"""

import pytest

from config import config
import argparse

# 创建ArgumentParser对象
parser = argparse.ArgumentParser(description='testcase')

# 添加命令行参数，设置其为可选，添加默认值
parser.add_argument('--arg', type=str, default='test_json_protocol', help='测试脚本')

# 解析命令行参数
args = parser.parse_args()

# 获取参数值
arg = args.arg

if __name__ == '__main__':
    pytest.main(["-q", "{}.py".format(arg)])