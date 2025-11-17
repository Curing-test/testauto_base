#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   helmet.py
@Time   :   2025/01/20 16:27:37
@Author :   lee
@Version:   1.0
@Desc   :   模拟头盔锁
"""
from utils.gpio import DigitalInputDevice, DigitalOutputDevice
import time
import os
import sys
import threading
import traceback
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import xa_serial_tool
from utils.gpio_util import PIN
from utils.log_util import Logger

logger = Logger(level="info").logger

class HelmetLock:

    pass

class HelmetLock6(HelmetLock):

    def __init__(self, elapsed_time=1.0):
        super().__init__()
        self.unlock_pin    = DigitalInputDevice(PIN.HELMET_LOCK_6.unlock)  # 开锁
        self.lock_pin      = DigitalInputDevice(PIN.HELMET_LOCK_6.lock)      # 关锁
        self.induction_pin = DigitalOutputDevice(PIN.HELMET_LOCK_6.induction)    # 感应
        self.ready_pin     = DigitalOutputDevice(PIN.HELMET_LOCK_6.ready)    # 到位
        # 设置引脚模式
        self.elapsed_time = elapsed_time-0.2    # 预留0.2s缓冲时间
        self.isblocked    = False  # 锁堵塞状态, Fasle为未堵塞，True为堵塞
        self.in_position_state = True   # 头盔在位状态
        self.unlock_state = False         # 头盔锁解锁状态，1为解锁状态，0为上锁状态
        lock_thread       = threading.Thread(target=self.run,daemon=True) # 启动一个守护线程，用于处理开关锁操作及状态检测
        lock_thread.start()


    def check_voltage(self):
        """
        读取开关锁电压差，进行开关锁操作
        """
        # 读取引脚A和B的电压
        helmet_unlock__voltage = self.unlock_pin.value  # 获取开锁引脚的电压值
        helmet_lock_voltage    = self.lock_pin.value    # 获取关锁引脚的电压值
        voltage_diff = helmet_unlock__voltage - helmet_lock_voltage # 
        # 根据电压差控制引脚C
        if voltage_diff == 1: 
            start_time = time.time()
            while self.unlock_pin.value - self.lock_pin.value == 1:
                elapsed_time = time.time() - start_time  # 计算持续时间
                if elapsed_time >= self.elapsed_time: 
                    logger.info("接收到开头盔锁信号")
                    if self.isblocked:
                        logger.info("头盔锁堵塞，开锁失败")
                    else:
                        logger.info("头盔锁开锁成功")
                        self.ready_pin.on()  # 设置到位引脚为高电平
                    break
                time.sleep(0.01)
        elif voltage_diff == -1:  
            start_time = time.time()
            while self.unlock_pin.value - self.lock_pin.value == -1:
                elapsed_time = time.time() - start_time  # 计算持续时间
                if elapsed_time >= self.elapsed_time: 
                    logger.info("接收到关头盔锁信号")
                    if self.isblocked:
                        logger.info("头盔锁堵塞，关锁失败")
                    else:
                        # if not self.in_position_state:
                        #     logger.info("头盔不在位，头盔锁关闭失败")
                        # else:
                        logger.info("头盔锁关锁成功")
                        self.ready_pin.off()  # 设置到位引脚为低电平
                    break
                time.sleep(0.01)

    def check_unlock_state(self):
        """
        判断头盔锁上锁状态
        """
        state = self.ready_pin.value
        if state:
            # print("头盔锁开启")
            self.unlock_state = True
        if not state:
            # print("头盔锁关闭")
            self.unlock_state = False
        return self.unlock_state

    def set_unlock_state(self,unlock_state=True):
        """配置头盔锁上锁状态
        Args:
            unlock_state (_type_): _description_
        """        
        if unlock_state:
            self.ready_pin.on()
        else:
            self.ready_pin.off()

    def check_induction_state(self):
        """
        判断头盔锁在位状态
        """
        state = self.induction_pin.value
        if state:
            # print("头盔离位")
            self.in_position_state = False
        if not state:
            # print("头盔在位")
            self.in_position_state = True
        return self.in_position_state

    def set_induction_state(self, induction_state=True):
        """配置头盔锁在位状态
        Args:
            induction_state (bool, optional): _description_. Defaults to True.
        """        
        if induction_state:
            self.induction_pin.off()  # 设置感应引脚为低电平，表示头盔在位
        else:
            self.induction_pin.on()  # 设置感应引脚为高电平，表示头盔离位

    def pickup_helmet(self):
        """拿取头盔
        """    
        # 头盔离位    
        self.induction_pin.on()  # 设置感应引脚为高电平，表示头盔离位
        time.sleep(0.5)
        logger.info("头盔已离位")

    def restore_helmet(self):
        """
        归还头盔
        """
        # 头盔在位
        self.induction_pin.off()  # 设置感应引脚为低电平，表示头盔在位
        time.sleep(0.5)
        logger.info("头盔已归还")


    def lock(self):
        """头盔锁上锁
        """        
        self.ready_pin.off()  # 设置到位引脚为低电平，表示头盔锁上锁
        time.sleep(0.5)
        logger.info("头盔已上锁")

    def unlock(self):
        """头盔锁解锁
        """        
        self.ready_pin.on()  # 设置到位引脚为高电平，表示头盔锁解锁
        time.sleep(0.5)
        logger.info("头盔已解锁")

    def run(self):
        while True:
            try:
                self.check_voltage()
                self.check_induction_state()
                self.check_unlock_state()
                time.sleep(0.1)  # 每0.1秒检查一次电压
            except Exception as e:
                print(traceback.format_exc())


class Helmet12:

    def __init__(self, serial):
        self.serial = serial
        self.type   = 12
        self.magic  = "AA 55"
        self.addr   = "06"     # 头盔锁地址
        # 连接状态
        self.connected = True
        # 基础信息
        self.protocol_version    = "01"            # 协议版本号
        self.manufacturer        = "XAfake"        # 生产厂家
        self.model               = "FakeH12"       # 头盔锁型号
        self.helmet_lock_version = "1.1.1"         # 头盔版本号[大端]
        self.lock_id             = "38F3ABA8E7DC"  # 蓝牙mac地址
        self.S_ID                = "F09E4A62B862"  # 头盔锁ID串号，亦即头盔蓝牙mac地址[大端]
        self.tk_voltage          = 2.5               # 头盔锁电压
        # 状态信息
        self.lock_state      = True   # 头盔锁逻辑状态 0:解锁 1:上锁
        self.induction_state = True   # 头盔磁感应状态 0:无头盔 1:有头盔
        self.ready_state     = True   # 头盔锁锁销到位 0:解锁位置 1:上锁位置
        self.wear_state      = False  # 头盔佩戴状态 0:未佩戴 1:已佩戴
        self.restore_state   = True   # 归还头盔结果 0:还盔失败 1:还盔成功 
        self.lock_block      = False  # 锁是否卡住 0:未卡住 1:卡住，如果锁卡住，开锁时不能打开
        # 锁自动操作
        self.is_auto_lock    = False  # 是否自动上锁 0:不自动上锁 1:自动上锁
        self.is_auto_open    = False  # 上锁失败是否自动开锁 0:不自动开锁  1:自动开锁
        # 头盔锁功能
        self.ble_support       = False  # BLE功能 0:不支持，1:支持
        self.RFID_support      = False  # RFID功能 0:不支持，1:支持
        self.induction_support = True   # 感应锁销 0:不支持，1:支持
        self.wear_support      = True   # 头盔佩戴检测 0:不支持，1:支持
        state_thread = threading.Thread(target=self.change_helmet_state, daemon=True)
        state_thread.start()

    def connect(self):
        """接上头盔锁
        """        
        self.connected = True

    def disconnect(self):
        """断开头盔锁连接
        """        
        self.connected = False

    def pick_up_helmet(self):
        """拿取头盔(开头盔锁、锁销离位状态)
        """     
        if not self.lock_state and not self.ready_state:
            self.induction_state = False
            return True
        print("头盔锁上锁或锁销上锁位置，无法拿取头盔")
        return False 

    def restore_helmet(self):
        """归还头盔
        """        
        if self.lock_state and self.ready_state:
            self.induction_state = True
            self.restore_state = True
            return True
        print("头盔锁未上锁或锁销未离位，无法归还头盔")
        return False

    def wear_helmet(self):
        """佩戴头盔
        """
        self.wear_state = True
    
    def take_off_helmet(self):
        """脱下头盔
        """
        self.wear_state = False

    def change_helmet_state(self):
        """改变头盔状态
        """
        while True:
            if self.is_auto_lock and not self.lock_state and self.ready_state:
                self.lock_helmet()
            if self.is_auto_open and self.lock_state and not self.induction_state:
                self.unlock_helmet()
            time.sleep(0.5)

    def deal_serial_data(self, cmd, data):
        """处理串口数据
        Args:
            cmd(str): [串口命令字]
            data ([type]): [description]
        """ 
        if not self.connected:
            return
        if cmd == "05":   # 解锁头盔锁
            self.serial_unlock_helmet(data)
        elif cmd == "06":   #  上锁头盔锁
            self.serial_lock_helmet(data)
        elif cmd == "15":   # 获取头盔基本信息
            self.helmet_base_info()
        elif cmd == "16":   # 获取头盔实时信息
            self.helmet_info_realtime()
        else:
            pass

    def version_2_hex_str(self, version):
        """版本号转16进制字符串
        Args:
            version (str): 版本号
        Returns:
            str: 16进制字符串
        """ 
        return " ".join([xa_serial_tool.int_to_hex_str(x) for x in version.split(".")])

    def set_block(self, block=False):
        """设置锁是否卡住
        Args:
            block (bool, optional): _description_. Defaults to False.
        """        
        self.lock_block = block     # 锁是否卡住 0:未卡住 1:卡住

    def unlock_helmet(self):
        """解锁头盔锁逻辑处理，
        开锁后：未上锁状态，感应到位，锁销解锁位置，未佩戴状态
        """
        self.lock_state      = False  # 头盔锁逻辑状态 0:解锁 1:上锁
        self.induction_state = True   # 头盔磁感应状态 0:无头盔 1:有头盔
        self.ready_state     = False  # 头盔锁锁销到位 0:解锁位置 1:上锁位置
        self.wear_state      = False  # 头盔佩戴状态 0:未佩戴 1:已佩戴
        self.restore_state   = False  # 归还头盔结果 0:还盔失败 1:还盔成功

    def lock_helmet(self):
        """上锁头盔锁逻辑处理，
        上锁后：上锁状态，感应到位，锁销上锁位置，已佩戴状态
        """
        self.lock_state      = True   # 头盔锁逻辑状态 0:解锁 1:上锁
        self.induction_state = True   # 头盔磁感应状态 0:无头盔 1:有头盔
        self.ready_state     = True   # 头盔锁锁销到位 0:解锁位置 1:上锁位置
        self.wear_state      = False  # 头盔佩戴状态 0:未佩戴 1:已佩戴
        self.restore_state   = True   # 归还头盔结果 0:还盔失败 1:还盔成功

    def helmet_base_info(self):
        """0x15 获取头盔基本信息响应
        """
        cmd                     = "15"
        manufacturer_hex        = xa_serial_tool.char_2_hex_str(self.manufacturer, length=8)                                                                                  #  厂商
        model_hex               = xa_serial_tool.char_2_hex_str(self.model, length=8)                                                                                         # 型号
        helmet_lock_version_hex = self.version_2_hex_str(self.helmet_lock_version)# 头盔锁版本号
        S_ID_hex                = " ".join([self.S_ID[i:i+2] for i in range(0, len(self.S_ID), 2)])                                                                           # 头盔锁ID
        reserved                = xa_serial_tool.protocol_reserved(10)
        sw                      = xa_serial_tool.bit_list_2_hex_str([int(self.ble_support), int(self.RFID_support), int(self.induction_support), int(self.wear_support)], 2)
        reversed_2              = xa_serial_tool.protocol_reserved(7)
        base_info               = f"{self.protocol_version} {manufacturer_hex} {model_hex} {helmet_lock_version_hex} {S_ID_hex} {reserved} {sw} {reversed_2}"
        length                  = xa_serial_tool.int_to_hex_str(len(base_info.split(" ")))
        check_sum               = xa_serial_tool.checksum(f"{self.addr} {cmd} {length} {base_info}")
        helmet_info_msg         = f"{self.magic} {self.addr} {cmd} {length} {base_info} {check_sum}"
        self.serial.write(bytes.fromhex(helmet_info_msg))
        return helmet_info_msg

    def serial_unlock_helmet(self, data):
        """0x05 解锁头盔锁
        """    
        cmd    = "05"  # 命令
        length = "01"  # 数据长度
        self.is_auto_lock = bool(int(data[1]))
        if not self.lock_block:
            code = 0
        else:
            code = 1
        self.unlock_helmet()
        check_sum   = xa_serial_tool.checksum(f"{self.addr} {cmd} {length} {xa_serial_tool.int_to_hex_str(code)}")
        serial_data = f"{self.magic} {self.addr} {cmd} {length} {xa_serial_tool.int_to_hex_str(code)} {check_sum}"
        self.serial.write(bytes.fromhex(serial_data))

    def serial_lock_helmet(self, data):
        """0x06 上锁头盔锁
        """        
        cmd    = "06"
        length = "01"
        self.is_auto_open = bool(int(data[1]))  
        if not self.lock_block:
            code = 0
        else:
            code = 1
        self.lock_helmet()
        check_sum   = xa_serial_tool.checksum(f"{self.addr} {cmd} {length} {xa_serial_tool.int_to_hex_str(code)}")
        serial_data = f"{self.magic} {self.addr} {cmd} {length} {xa_serial_tool.int_to_hex_str(code)} {check_sum}"
        print(serial_data)
        self.serial.write(bytes.fromhex(serial_data))

    def helmet_info_realtime(self):
        """0x16 获取头盔实时信息
        """       
        cmd             = "16"
        sw              = xa_serial_tool.bit_list_2_hex_str([int(self.lock_state), int(self.induction_state), int(self.ready_state), 0,0,self.wear_state,self.restore_state], 1)
        reversed        = xa_serial_tool.protocol_reserved(9)
        tk_version      = self.version_2_hex_str(self.helmet_lock_version)
        custom_id       = "00 00"                                                                                                                                                                    # 客户ID
        sensitivity     = "00"                                                                                                                                                                       # 灵敏度等级
        sensor_state    = "00"                                                                                                                                                                       # 传感器状态#
        fault1          = "00"
        fault2          = "00"
        sw1             = xa_serial_tool.bit_list_2_hex_str([int(self.wear_state)], 1)
        tk_voltage      = xa_serial_tool.int_to_hex_str(int(self.tk_voltage*100))
        print(tk_voltage)
        tk_id           = " ".join([self.lock_id[i:i+2] for i in range(0, len(self.lock_id), 2)])
        length          = xa_serial_tool.int_to_hex_str(len(f"{sw} {reversed} {tk_version} {custom_id} {sensitivity} {sensor_state} {fault1} {fault2} {sw1} {tk_voltage} {tk_id}".split(" ")))
        check_sum       = xa_serial_tool.checksum(f"{self.addr} {cmd} {length} {sw} {reversed} {tk_version} {custom_id} {sensitivity} {sensor_state} {fault1} {fault2} {sw1} {tk_voltage} {tk_id}")
        helmet_info_msg = f"{self.magic} {self.addr} {cmd} {length} {sw} {reversed} {tk_version} {custom_id} {sensitivity} {sensor_state} {fault1} {fault2} {sw1} {tk_voltage} {tk_id} {check_sum}"
        self.serial.write(bytes.fromhex(helmet_info_msg))
        return helmet_info_msg

if __name__ == "__main__":
    helmet = HelmetLock6()
    # time.sleep(20)
    # helmet.lock()
    time.sleep(10)
    helmet.unlock()
    time.sleep(10)
    helmet.pickup_helmet()
    time.sleep(10)
    # helmet.restore_helmet()
    # time.sleep(10)
    # helmet.lock()
    time.sleep(10) 