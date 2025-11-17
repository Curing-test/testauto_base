#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   bms.py
@Time   :   2025/03/25 09:36:08
@Author :   lee
@Version:   1.0
@Desc   :   None
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from utils import xa_serial_tool
class BMS:
    pass

class BMS0:

    def connect(self):
        pass

    def disconnect(self):
        pass

class XingHengBMS:
    def __init__(self, serial, sn="XIAOAN-FAKE-BMS4"):
        self.serial                  = serial                                # 串口总线，传入485或者UART
        self.type                    = 4                                     # BMS类型，星恒BMStype为4
        self.start_symbol            = "3A"                                  # 星恒协议起始位
        self.addr                    = "16"                                  # 星恒bms命令字
        self.stop_symbol             = "0D 0A"                               # 星恒协议结束位
        self.battery_temperature     = 36.5                                  # 电池内部温度：摄氏度
        self.mos_temperature         = 37.0
        self.battery_temperature_min = 33.0                                  # 电池最低温度
        self.env_temperature         = 25.0                                  # 环境温度
        self.v33_temperature         = 24.0
        self.connect_status          = False                                 # BMS是否接入，默认未接入，接大电，开电门状态下开始发送数据
        self.sn                      = sn                                    # 电池SN号
        self.battery_voltage         = 53600                                 # 电池组总电压，单位mV
        self.realtime_current        = 100                                   # 实时电流，单位mA
        self.relatice_capacity       = 25                                    # 相对容量  百分比
        self.remain                  = 13306                                 # 剩余容量数值，单位mAh
        self.capacity                = 53600                                 # 满电容量，单位mAH
        self.cycle                   = 42                                    # 循环次数，单位周
        self.cell_1_7_voltage        = [3897,3896,3895,3894,3893,3892,3891]  # 1~7节电池电压，单位mV
        self.cell_8_13_voltage       = [3908,3909,3910,3911,3912,3913]       # 8~13节电池电压，单位mV
        self.soh                     = 99                                    # SOH
        self.software_version        = 254                                   # 软件版本号
        self.hardware_version        = 254                                   # 硬件版本号
        self.bms_version             = 254                                   # BMS版本号

    def check_sum(self, data):
        """星恒BMS校验和，小端字节序
        Args:
            data (str): 转化成str的数据内容，不含地址位
        """
        data = f"{self.addr} {data}"
        checksum  = sum([int(i, 16) for i in data.split(" ")])
        low_byte  = xa_serial_tool.int_to_hex_str(checksum & 0xFF)         # 低字节
        high_byte = xa_serial_tool.int_to_hex_str((checksum >> 8) & 0xFF)  # 高字节
        return f"{low_byte} {high_byte}"
    
    def connect(self):
        """接入BMS
        """        
        self.connect_status = True

    def disconnect(self):
        """断开BMS
        """        
        self.connect_status = False

    def deal_serial(self, serial_data):
        """处理串口数据返回信息
        """        
        if not self.connect_status:
            print("BMS未连接状态,不予响应")
            return
        command = serial_data[2]
        print("*"*30)
        print(f"收到{command}")
        print("*"*30)
        if   command == "08":
            self.response_battery_temperature()
        elif command == "09":
            self.response_battery_voltage()
        elif command == "0A":
            self.response_realtime_current()
        elif command == "0D":
            self.response_relatice_capacity()
        elif command == "0F":
            self.response_remain()
        elif command == "10":
            self.response_capacity()
        elif command == "17":
            self.response_cycle()
        elif command == "23":
            self.response_bms_version()
        elif command == "24":
            self.response_cell_1_7_voltage()
        elif command == "25":
            self.response_cell_8_13_voltage()
        elif command == "0C":
            self.reponse_soh()
        elif command == "7F":
            self.response_version()
        elif command == "7E":
            self.response_battery_id()
        else:
            print(f"指令{command}未实现")

        
    def assemble_serial_frame(self, command, data, hex_len, byteorder='little'):
        """组装串口帧数据
        Args:
            command (_type_): 命令字
            data (_type_): 具体数据
            hex_len (_type_): 字段长度
            byteorder (_type_): 大小端字节序，默认小端
        """        
        data        = xa_serial_tool.int_to_hex_str(data, hex_len=hex_len, byteorder=byteorder)
        length      = xa_serial_tool.int_to_hex_str(len(data.split(" ")))
        checksum    = self.check_sum(f'{command} {length} {data}')
        serial_data = f"{self.start_symbol} {self.addr} {command} {length} {data} {checksum} {self.stop_symbol}"
        # print(f"SEND: {serial_data}")
        self.serial.write(bytes.fromhex(serial_data))
        return serial_data
    
    def response_battery_temperature(self):
        """0x08 电池组内部温度，分辨率0.1K，单位K
        """    
        command             = "08"
        battery_temperature = xa_serial_tool.int_to_hex_str(self.battery_temperature, hex_len=2, byteorder='little')
        # battery_temperature_max        = xa_serial_tool.int_to_hex_str(self.battery_temperature_max, hex_len=2, byteorder='little')
        mos_temperature         = xa_serial_tool.int_to_hex_str(self.mos_temperature, hex_len=2, byteorder='little')
        battery_temperature_min = xa_serial_tool.int_to_hex_str(self.battery_temperature_min, hex_len=2, byteorder='little')
        env_temperature         = xa_serial_tool.int_to_hex_str(self.env_temperature, hex_len=2, byteorder='little')
        v33_temperature         = xa_serial_tool.int_to_hex_str(self.v33_temperature, hex_len=2, byteorder='little')
        data                    = f"{battery_temperature} {mos_temperature} {battery_temperature_min} {env_temperature} {v33_temperature}"
        length                  = xa_serial_tool.int_to_hex_str(len(data.split(" ")))
        checksum                = self.check_sum(f'{command} {length} {data}')
        serial_data             = f"{self.start_symbol} {self.addr} {command} {length} {data} {checksum} {self.stop_symbol}"
        # print(f"SEND: {serial_data}")
        self.serial.write(bytes.fromhex(serial_data))
        return serial_data

    def response_battery_voltage(self):
        """0x09 电池组总电压，单位mV
        """   
        return self.assemble_serial_frame(command='09', data=self.battery_voltage, hex_len=4, byteorder='little')     

    def response_realtime_current(self):
        """0x0a 实时电流，单位mA
        """    
        return self.assemble_serial_frame(command='0A', data=self.realtime_current, hex_len=4, byteorder='little')

    def response_relatice_capacity(self):
        """0x0d 相对容量  百分比
        """   
        return self.assemble_serial_frame(command='0D', data=self.relatice_capacity, hex_len=2, byteorder='little')
        
    def response_remain(self):
        """0x0f 剩余容量数值，单位mAh
        """    
        return self.assemble_serial_frame(command='0F', data=self.remain, hex_len=2, byteorder='little')    

    def response_capacity(self):
        """0x10 满电容量，单位mAH
        """       
        return self.assemble_serial_frame(command='10', data=self.capacity, hex_len=2, byteorder='little')  

    def response_cycle(self):
        """0x17 循环次数，单位周
        """       
        return self.assemble_serial_frame(command='17', data=self.cycle, hex_len=2, byteorder='little') 

    def response_cell_1_7_voltage(self):
        """0x24 1~7节电池电压，单位mV
        """       
        command     = "24"
        data        = " ".join(xa_serial_tool.int_to_hex_str(d, hex_len=2, byteorder="little") for d in self.cell_1_7_voltage)
        length      = xa_serial_tool.int_to_hex_str(len(data.split(" ")))
        checksum    = self.check_sum(f'{command} {length} {data}')
        serial_data = f"{self.start_symbol} {self.addr} {command} {length} {data} {checksum} {self.stop_symbol}"
        self.serial.write(bytes.fromhex(serial_data))
        # print(f"SEND: {serial_data}")
        return serial_data

    def response_cell_8_13_voltage(self):
        """0x25 8~13节电池电压，单位mV
        """ 
        command     = "25"
        data        = " ".join(xa_serial_tool.int_to_hex_str(d, hex_len=2, byteorder="little") for d in self.cell_8_13_voltage)
        length      = xa_serial_tool.int_to_hex_str(len(data.split(" ")))
        checksum    = self.check_sum(f'{command} {length} {data}')
        serial_data = f"{self.start_symbol} {self.addr} {command} {length} {data} {checksum} {self.stop_symbol}"
        self.serial.write(bytes.fromhex(serial_data))
        # print(f"SEND: {serial_data}")
        return serial_data     

    def reponse_soh(self):
        """0x0C SOH
        """   
        return self.assemble_serial_frame(command='0C', data=self.soh, hex_len=2, byteorder='little')

    def response_version(self):
        """0x7F 版本号 100~255之间
        """      
        command     = "7F"
        data        = f"00 {xa_serial_tool.int_to_hex_str(self.software_version,1)} {xa_serial_tool.int_to_hex_str(self.hardware_version,1)}"
        length      = xa_serial_tool.int_to_hex_str(len(data.split(" ")))
        checksum    = self.check_sum(f'{command} {length} {data}')
        serial_data = f"{self.start_symbol} {self.addr} {command} {length} {data} {checksum} {self.stop_symbol}"
        # print(f"SEND: {serial_data}")
        self.serial.write(bytes.fromhex(serial_data))
        return serial_data 

    def response_battery_id(self):
        """0x7E 电池组ID条码
        """         
        command     = "7E"
        data        = " ".join(xa_serial_tool.char_2_hex_str(d) for d in self.sn)
        length      = xa_serial_tool.int_to_hex_str(len(data.split(" ")))
        checksum    = self.check_sum(f'{command} {length} {data}')
        serial_data = f"{self.start_symbol} {self.addr} {command} {length} {data} {checksum} {self.stop_symbol}"
        # print(f"SEND: {serial_data}")
        self.serial.write(bytes.fromhex(serial_data))
        return serial_data 
    
    def response_bms_version(self):
        """0x23 BMS版本号
        """              
        return self.assemble_serial_frame(command='23', data=self.capacity, hex_len=8, byteorder='little') 


class XiaoAnBMS:
    def __init__(self, serial):
        self.serial = serial
        self.type = 1
        self.magic = "AA 55"
        self.addr = "01"

    def heart_beat(self):
        """ 0x0A 心跳
        """        

    def query_bms_base_info(self):
        """0x15 查询电池基础信息
        """        

    def query_bms_realtime_info(self):
        """0x16 查询电池实时信息
        """        
        
class SerialTTT:

    def write(self, data):
        # print(data)
        pass

if __name__ == "__main__":
    s = SerialTTT()
    xingheng = XingHengBMS(serial=s)
    print(xingheng.check_sum("08 04 7E 0B 00 00"))
    print(xingheng.check_sum("08 04 CA 0D 00 00"))# 3A 16 08 04 CA 0D 00 00 F9 00 0D 0A
    # print(xingheng.response_battery_temperature())
    # print(xingheng.response_battery_voltage())
    # print(xingheng.response_realtime_current())
    # print(xingheng.response_battery_id())