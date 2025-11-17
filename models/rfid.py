#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   rfid.py
@Time   :   2025/03/20 14:59:52
@Author :   lee
@Version:   1.0
@Desc   :   模拟RFID
"""
import os
import sys
import threading
import time
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import xa_serial_tool
from utils.gpio_util import PIN
from utils.gpio import DigitalInputDevice, DigitalOutputDevice

class RFID:

    def __init__(self, serial, type="01", version="1.70.52", protocolVer="01", card_id=""):
        self.acc_pin = DigitalInputDevice(PIN.RFID.acc) # RFID 5V引脚定义
        self.acc_status     = False        # RFID电源状态
        self.serial         = serial       # 指定串口，可传入485或者UART
        self.connect_status = False        # RFID连接状态, 默认未连接状态
        self.type           = type         # 模块类型，并决定后续数据结构，1：高频模块，2：超高频模块
        self.card_id = card_id
        # if self.type == "01":
        #     self.card_id = "AA" * 8
        # elif self.type == "02":
        #     self.card_id = "AA" * 12 
        self.version        = version      # RFID版本号
        self.protocolVer    = protocolVer  # 协议版本号，默认为1
        self.magic          = "AA 55"
        self.addr           = "20"
        threading.Thread(target=self.check_voltage, daemon=True).start()

    def deal_serial(self, serial_data):
        """处理RFID总线上串口数据，用于功能分配
        """        
        if not self.connect_status or not self.acc_status:
            # print("RFID未连接或电源没接，无需处理")
            return
        if serial_data[0] == "AA" and serial_data[1] == "55":
            command = serial_data[3]
            if command == "11":
                # print("-"*30)
                # print("开始回复RFID信息")
                # print("-"*30)
                self.query_module_infomation()
        elif serial_data[0] == "FF" and serial_data[1] == "02":
            command = serial_data[2]
            if command == "00":
                self.response_query_card_id_ff02
            elif command == "04":
                self.response_query_version_ff02()
        elif serial_data[0] == "A0" and serial_data[1] == "03":
            command = serial_data[2]
            if command == "6A":
                self.response_query_version_a003()
            elif command == "B8":
                self.response_query_card_id_a003()


    ##########基本操作########
    def check_voltage(self):
        """检测RFID 5V引脚电压状态，高电平RFID已开启，低电平RFID未开启
        """       
        while True:
            status =self.acc_pin.value
            if status == 1:
                self.acc_status = True
            elif status == 0:
                self.acc_status = False
            # print(self.acc_status)
            time.sleep(1)

    def connect(self):
        """接入RFID
        """     
        self.connect_status = True   

    def disconnect(self):
        """断开RFID
        """        
        self.connect_status = False

    
    def pick_up_card(self):
        """移开标签卡
        """
        print("移除卡片")
        if self.type == "01":
            self.card_id = "00"*8
        if self.type == "02":
            self.card_id = "00"*12

    def set_card(self, card_id="FFEEDDCCBBAA998877665544"):
        """放置标签卡
        """       
        print(f"放置标签卡:{card_id}")
        self.card_id = card_id
    ########################## 

    ##########AA 55协议########
    def query_module_infomation(self):
        """ 0x11 查询模块信息
        """  
        command = "11"
        if self.card_id:
            card_id = ' '.join([self.card_id[i:i+2] for i in range(0,len(self.card_id),2)])
            data = f"{xa_serial_tool.int_to_hex_str(self.protocolVer)} {' '.join(xa_serial_tool.int_to_hex_str(x) for x in self.version.split('.'))} {xa_serial_tool.int_to_hex_str(self.type)} {card_id}"
        else:
            print("无卡")
            return 
        # print(f"----------------》》》》》》》》》》》： 「{data}」")
        length       = xa_serial_tool.int_to_hex_str(len(data.split(" ")))
        check_sum    = xa_serial_tool.checksum(f"{self.addr} {command} {length} {data}")
        serial_frame = f"{self.magic} {self.addr} {command} {length} {data} {check_sum}"
        # print(serial_frame)
        self.serial.write(bytes.fromhex(serial_frame))
        return serial_frame
    ##########################

    ##########FF02协议########
    def response_query_card_id_ff02(self):
        """FF 02 01 查询标签ID回复
        """   
        start_symbol = "FF 02"
        command      = "01"
        if self.card_id:
            card_id = " ".join([xa_serial_tool.char_2_hex_str(x) for x in self.card_id])
        else:
            card_id = "FF FF"
        length       = xa_serial_tool.int_to_hex_str(len(card_id.split(" ")))
        sum_crc16    = xa_serial_tool.calculate_crc16(f"{start_symbol} {command} {length} {card_id}")
        serial_frame = f"{start_symbol} {command} {length} {card_id} {sum_crc16}"
        self.serial.write(bytes.fromhex(serial_frame))
        return serial_frame
    
    def response_query_version_ff02(self):
        """FF 02 05 查询版本应答
        """   
        start_symbol = "FF 02"
        command      = "05"
        version      = " ".join([xa_serial_tool.int_to_hex_str(x) for x in self.version.split(".")])
        length       = xa_serial_tool.int_to_hex_str(len(version.split(" ")))
        sum_crc16    = xa_serial_tool.calculate_crc16(f"{start_symbol} {command} {length} {version}")
        serial_frame = f"{start_symbol} {command} {length} {version} {sum_crc16}"
        self.serial.write(bytes.fromhex(serial_frame))
        return serial_frame

    ##########################

    ##########A0 03协议#########
    def response_query_version_a003(self):
        start_symbol = "E0"
        command      = "6A"
        device       = "00"
        version      = " ".join([xa_serial_tool.int_to_hex_str(x) for x in self.version.split(".")])
        length       = xa_serial_tool.int_to_hex_str(len(version.split(" "))+3)                       # 版本号+设备号+命令字+校验和
        checksum     = xa_serial_tool.checksum(f"{start_symbol} {command} {length} {version}")
        serial_frame = f"{start_symbol} {length} {command} {device} {version} {checksum}"
        self.serial.write(bytes.fromhex(serial_frame))
        return serial_frame
    
    def response_query_card_id_a003(self):
        if not self.card_id:
            serial_frame = "E4 04 B8 00 01 5F"
        else:
            start_symbol = "E0"
            command      = "B8"
            version      = " ".join([xa_serial_tool.int_to_hex_str(x) for x in self.version.split(".")])
            length       = xa_serial_tool.int_to_hex_str(len(version.split(" ")))
            sum_crc16    = xa_serial_tool.calculate_crc16(f"{start_symbol} {command} {length} {version}")
            serial_frame = f"{start_symbol} {command} {length} {version} {sum_crc16}"
        self.serial.write(bytes.fromhex(serial_frame))
        return serial_frame

    ##########################

class SerialTTT:

    def write(self, data):
        # print(data)
        pass
if __name__ == "__main__":
    serial = SerialTTT()
    rfid = RFID(serial) 
    rfid.card_id = ""
    # print(rfid.response_query_card_id_ff02())
    # print(rfid.response_query_version_ff02())
    
    while True:
        time.sleep(1)

    