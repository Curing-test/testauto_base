#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   externalPower.py
@Time   :   2025/02/06 14:12:52
@Author :   lee
@Version:   1.0
@Desc   :   外置电源（大电）控制
"""
from gpiozero import DigitalOutputDevice
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from models.bms import BMS0
from utils.gpio_util import PIN


class ExternalPower:

    def __init__(self, bms=None):
        """大电控制
        """
        if not bms:
            bms = BMS0()
        self.bms = bms
        self.power_pin = DigitalOutputDevice(PIN.ExternalPower.power)

    def disconnect(self):
        """断开大电
        """        
        self.bms.connect()
        self.power_pin.off()

    def connect(self):
        """接通大电
        """        
        self.power_pin.on()

if __name__ == "__main__":
    import time
    power = ExternalPower()
    power.connect()
    time.sleep(10)
    power.disconnect()
