#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   xiaoan_485_bus.py
@Time   :   2025/03/20 15:19:31
@Author :   lee
@Version:   1.0
@Desc   :   模拟设备处理中控485总线发来的数据
""" 
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models.overload import Overload2
import asyncio
from queue import Queue
import threading
import time
import serial
import time
import RPi.GPIO as GPIO
import time
from models.rfid import RFID
from models.bms import XingHengBMS
from models.helmetLock import Helmet12, HelmetLock6
from models.moter_controller import MotorController1

serial_queue = Queue(maxsize=200)

# 延迟初始化串口和相关设备，避免导入时设备不存在
ser = None
motor_controller = None
bms = None
helmet = None
rfid = None
ovld = Overload2()

def init_serial_port(port="/dev/ttyUSB0", baudrate=9600):
    """初始化串口和设备对象
    Args:
        port (str): 串口设备路径，默认 /dev/ttyUSB0
        baudrate (int): 波特率，默认 9600
    Returns:
        bool: 初始化成功返回True，失败返回False
    """
    global ser, motor_controller, bms, helmet, rfid
    try:
        if ser is None or not ser.is_open:
            ser = serial.Serial(port=port, baudrate=baudrate, timeout=1)
            print(f"串口 {port} 初始化成功")
        
        # 初始化设备对象
        if motor_controller is None:
            motor_controller = MotorController1(serial=ser)
            motor_controller.speed = 5
        
        if bms is None:
            bms = XingHengBMS(serial=ser)
            bms.connect()
        
        if helmet is None:
            helmet = Helmet12(serial=ser)
        
        if rfid is None:
            rfid = RFID(serial=ser)
            rfid.connect()
        
        return True
    except serial.SerialException as e:
        print(f"串口初始化失败: {e}")
        print(f"请确保串口设备 {port} 存在且可访问")
        return False
    except Exception as e:
        print(f"设备初始化失败: {e}")
        return False


def serial_reading():
    """串口读取线程函数"""
    while True:
        try:
            if ser is None or not ser.is_open:
                time.sleep(1)
                continue
            if ser.in_waiting > 0:
                serial_data = ser.read(ser.in_waiting).hex()
                if not serial_queue.full():
                    serial_queue.put(serial_data)
                else:
                    print("queue is full")
                time.sleep(0.01)
        except Exception as e:
            print(f"串口读取错误: {e}")
            time.sleep(1)

def deal_serial_data():
    while True:
        if not serial_queue.empty():
            serial_data = serial_queue.get()
            # print(f"recv: {serial_data}")
            asyncio.run(deal_one_frame(serial_data))
            time.sleep(0.01)

async def deal_one_frame(serial_data):
    """处理一帧串口数据
    Args:
        serial_data (str): 十六进制格式的串口数据
    """
    # TODO(默认每条数据都是完整的，暂不考虑数据分包问题)
    serial_list = [serial_data.upper()[i:i+2] for i in range(0, len(serial_data), 2)]
    # print(" ".join(serial_list))
    # 处理AA 55开头小安协议数据
    if len(serial_list) < 5:
        return
    if serial_list[0] == "AA" and serial_list[1] == "55":
        addr = serial_list[2]
        cmd = serial_list[3]
        data = serial_list[4:]
        if addr == "10":        # 小安控制器
            # print(f"控制器信息：{serial_list}")
            if motor_controller is not None:
                motor_controller.deal_one_serial(serial_list)
        elif addr == "06":      # YKT通信头盔锁
            if helmet is not None:
                helmet.deal_serial_data(cmd=cmd, data=data)
        elif addr == "20":      # RFID
            if rfid is not None:
                rfid.deal_serial(serial_list)
        await asyncio.sleep(0.05)
    elif serial_list[0] == "3A" and serial_list[1] == "16":
        # BMS信息
        print(f"BMS: {' '.join(serial_list)}")
        if bms is not None:
            bms.deal_serial(serial_list)
    elif serial_list[0] == "FF" and serial_list[1] == "02":
        if rfid is not None:
            rfid.deal_serial(serial_list)
    elif serial_list[0] == "A0" and serial_list[1] == "03":
        if rfid is not None:
            rfid.deal_serial(serial_list)
    else:
        print(f"该指令对应设备未实现：{serial_list}")

def main(port="/dev/ttyUSB0", baudrate=9600):
    """启动串口总线处理
    Args:
        port (str): 串口设备路径，默认 /dev/ttyUSB0
        baudrate (int): 波特率，默认 9600
    """
    # 初始化串口和设备
    if not init_serial_port(port=port, baudrate=baudrate):
        print("串口初始化失败，无法启动串口总线处理")
        return False
    
    # 启动串口读取和处理线程
    read_thread = threading.Thread(target=serial_reading, daemon=True)
    deal_thread = threading.Thread(target=deal_serial_data, daemon=True)
    read_thread.start()
    deal_thread.start()
    print("串口总线处理已启动")
    return True

if __name__ == "__main__":
    from models.externalPower import ExternalPower
    externalPower = ExternalPower()
    externalPower.connect()  # 接通大电
    main()
    while True:
        time.sleep(1)