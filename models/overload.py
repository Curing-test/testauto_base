#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   overload.py
@Time   :   2025/02/23 16:03:49
@Author :   lee
@Version:   1.0
@Desc   :   超载模拟相关
"""

import time
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.gpio_util import PIN
from utils.log_util import Logger
from utils.gpio import DigitalInputDevice, DigitalOutputDevice, PWMOutputDevice

logger = Logger(level="info").logger
class Overload:
    pass


class Overload2:
    
    def __init__(self):
        self.head_pin = DigitalOutputDevice(PIN.OVERLOAD_2.head)    # 前触点
        self.tail_pin  = DigitalOutputDevice(PIN.OVERLOAD_2.tail)    # 后触点

    def trig_head(self):
        """触发前触点
        """        
        self.head_pin.on()

    def trig_tail(self):
        """触发后触点
        """        
        self.tail_pin.on()

    def loose_head(self):
        """释放前触点
        """        
        self.head_pin.off()  # 使用 DigitalOutputDevice 的 off 方法来松开触点
    
    def loose_tail(self):
        """释放后触点
        """        
        self.tail_pin.off()

if __name__ == "__main__":
    ovld = Overload2()
    # ovld.trig_head()
    # ovld.trig_tail()
    # ovld.loose_head()
    # ovld.loose_tail()
    while True:
        ovld.trig_head()
        ovld.trig_tail()
        time.sleep(3)
        ovld.loose_head()
        ovld.loose_tail()
        time.sleep(1)