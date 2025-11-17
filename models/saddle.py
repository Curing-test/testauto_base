#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   saddle.py
@Time   :   2025/01/20 16:27:30
@Author :   lee
@Version:   1.0
@Desc   :   模拟电池仓锁
"""
import traceback
import time
import os
import sys
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.gpio_util import PIN
from utils.log_util import Logger
from utils.gpio import DigitalInputDevice, DigitalOutputDevice


logger = Logger(level="info").logger
class Saddle:
    pass

class SaddleType1(Saddle):
    def __init__(self,elapsed_time=1.0):
        self.lock_pin      = DigitalInputDevice(PIN.SADDLE_LOCK_1.lock) # 上锁
        self.unlock_pin    = DigitalInputDevice(PIN.SADDLE_LOCK_1.unlock)   # 解锁
        self.feedback_pin  = DigitalOutputDevice(PIN.SADDLE_LOCK_1.feedback) # 反馈
        self.unlock_status = False  # 开锁状态, 0为开锁，1为关锁
        self.elapsed_time  = elapsed_time-0.2   # 减掉0.2s缓冲时间
        self.reset_state   = False      # 复位状态
        self.check_state()    # 初始化一下解锁状态
        self.isblocked = False  # 锁堵塞状态, Fasle为未堵塞，True为堵塞
        lock_thread    = threading.Thread(target=self.run, daemon=True) # 启动一个守护线程，用于处理开关锁操作及状态检测
        lock_thread.start()

    def check_voltage(self):
        """根据开关锁引脚电压信号控制锁的开关
        Returns:
            _type_: _description_
        """        
        saddle_unlock_voltage = self.unlock_pin.value
        saddle_lock_voltage   = self.lock_pin.value
        voltage_diff = saddle_unlock_voltage - saddle_lock_voltage
        if voltage_diff == 1:  # 开锁引脚为高电平，关锁引脚为低电平，电压差为+5V
            start_time = time.time()
            while self.unlock_pin.value - self.lock_pin.value == 1:
                elapsed_time = time.time() - start_time  # 计算持续时间
                if elapsed_time >= self.elapsed_time:  # 判断是否持续了1秒
                    logger.info("接收到开电池仓锁信号")
                    if self.isblocked:
                        logger.info("电池仓锁堵塞，开锁失败")
                    else:
                        self.feedback_pin.on()  # 模拟开锁反馈
                        logger.info("电池仓锁开锁成功")
                    break
                time.sleep(0.01)
        elif voltage_diff == -1:  # A为低电平，B为高电平，电压差为-5V
            start_time = time.time()
            while self.unlock_pin.value - self.lock_pin.value == -1:
                elapsed_time = time.time() - start_time  # 计算持续时间
                if elapsed_time >= self.elapsed_time:  # 判断是否持续了1秒
                    logger.info("接收到复位电池仓锁指令")
                    self.reset_state = True
                    break
                time.sleep(0.01)

    def set_reset_state(self, reset_state=False):
        """设置复位状态
        Args:
            reset_state (bool, optional): _description_. Defaults to False.
        """        
        self.reset_state = reset_state

    def get_reset_state(self):
        """获取电池仓锁复位状态
        Returns:
            _type_: _description_
        """
        return self.reset_state

    def set_blocked(self, isblocked=False):
        """设置锁堵塞状态
        Args:
            isblocked (bool, optional): _description_. Defaults to False.
        """    
        self.isblocked = isblocked

    def check_state(self):
        """检查头盔锁的状态
        Returns:
            state: boolean，锁的状态
        """        
        self.unlock_status = self.feedback_pin.value  # 获取反馈引脚的电压状态
        # print(self.unlock_status)
        return self.unlock_status

    def lock(self, isblocked=False):
        """上锁，模拟人工压下锁
        Args:
            isblocked (bool, optional): _description_. Defaults to False.
        """        
        if not isblocked:
            self.feedback_pin.off()  # 模拟关锁反馈
            self.unlock_status = True    # 关锁成功
            logger.info("关电池仓锁成功")
        else:
            self.unlock_status = self.check_state()    # 关锁成功
            logger.info("电池仓锁堵塞，关电池仓锁失败")

    def unlock(self, isblocked=False):
        """配置电池仓锁未锁状态
        Args:
            isblocked (bool, optional): _description_. Defaults to False.
        """        
        if not isblocked:
            self.feedback_pin.off()  # 模拟开锁反馈
            self.unlock_status = False    # 开锁成功
            logger.info("电池仓锁已开启")
        else:
            self.unlock_status = self.check_state()    # 关锁成功
            logger.info("电池仓锁堵塞，电池仓锁开启失败")


    def run(self):
        while True:
            try:
                self.check_voltage()
                self.check_state()
                time.sleep(0.1)  # 每0.1秒检查一次电压
            except:
                logger.error("电池仓锁检测异常")
                print(traceback.format_exc())


if __name__ == "__main__":
    saddle = SaddleType1()
    i = 0
    while True:
        time.sleep(30)
        saddle.lock()
    # saddle.run()
    # time.sleep(10)
    # for i in range(10):
    #     saddle.unlock()
    #     GPIO.output(saddle.feedback_pin, GPIO.HIGH)
    #     time.sleep(5)
    #     saddle.lock()
    #     GPIO.output(saddle.feedback_pin, GPIO.LOW)
    #     time.sleep(5)