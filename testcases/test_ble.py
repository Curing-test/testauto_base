from datetime import datetime
import os
import sys
import time
import asyncio

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models import excel_report, read_excel
from models.xiaoan_json import XiaoAnJson
from utils.buleez_tool import BluetoothHandler,imei_to_ble_addr
from config import config


class BLETest:
    def setup_class(self):
        # 执行测试前，创建excel
        self.test_suit_name   = "BLE测试"
        self.test_function    = "BLE测试"
        self.start_time_str   = str(datetime.now())[0:19].replace(":", "-")
        self.report_file_name = os.path.join(
            config.EXCEL_REPORT_PATH, f"{config.DEVICE_TYPE_CHANGE}_v{config.devVsn}-{self.test_suit_name}报告_{self.start_time_str}.xlsx")
        excel_report.generator_header(file_name=self.report_file_name,sheet_name=self.test_function)
        self.imei     = config.IMEI
        self.excutor  = XiaoAnJson()
        self.BLE_loop = asyncio.get_event_loop().run_until_complete
        self.bluetooth_handler = BluetoothHandler(imei_to_ble_addr(self.imei))


    def setup_method(self):
        # 每个用例执行前，初始化参数
        self.url         = ""
        self.description = ""
        self.method      = "POST"
        self.wait_time   = 0
        self.cardId      = ''
        self.payload     = {
                                "imei" : self.imei,
                                "async": 'false',
                                "cmd"  : {
                                    "c"    : 0,
                                    "param": {
                                    }
                                }
                            }
        self.excutor.c4(defend = 1)
        self.BLE_loop(self.bluetooth_handler.run())

    def teardown_method(self):
        pass

    def teardown_class(self):
        # 所有用例执行完成后，更新excel结果
        print("teardown_class")
    def test_ble_connect(self): 
        self.description = "ble_connect"
        ret = self.BLE_loop(self.bluetooth_handler.run())
        assert ret == True
    
    def test_ble_message(self):
        ret = self.BLE_loop(self.bluetooth_handler.send_data(0x2a)) #查询信息
        print(ret)
        assert ret != None
    
    def test_ble_acc1(self):
        self.excutor.c4(defend = 1) #设防
        self.BLE_loop(self.bluetooth_handler.send_data(0x2c)) #蓝牙启动
        time.sleep(1)
        ret = self.excutor.c34()
        assert ret['result.acc'] == 1
        assert ret["result.defend"] == 0

        self.BLE_loop(self.bluetooth_handler.send_data(0x2c)) #再次蓝牙启动
        time.sleep(1)
        ret = self.excutor.c34()
        assert ret['result.acc'] == 1
        assert ret["result.defend"] == 0
    
    def test_ble_acc0(self):
        self.excutor.c4(defend = 1) #设防
        self.BLE_loop(self.bluetooth_handler.send_data(0x2d)) #蓝牙熄火
        time.sleep(1)
        ret = self.excutor.c34()
        assert ret['result.acc'] == 0
        assert ret["result.defend"] == 0

        self.BLE_loop(self.bluetooth_handler.send_data(0x2d)) #再次蓝牙熄火
        ret = self.excutor.c34()
        assert ret['result.acc'] == 0
        assert ret["result.defend"] == 0
    
    def test_ble_defend1(self):
        self.excutor.c33(acc = 1) #开电门
        self.BLE_loop(self.bluetooth_handler.send_data(0x2b)) #蓝牙设防
        time.sleep(1)
        ret = self.excutor.c34()
        assert ret['result.acc'] == 0
        assert ret["result.defend"] == 1
    
    def test_ble_reboot(self):
        self.BLE_loop(self.bluetooth_handler.send_data(0x26)) #蓝牙重启
        ret = self.BLE_loop(self.bluetooth_handler.disconnect())
        time.sleep(30)
        assert ret == True

if __name__ == "__main__":
    pytest.main(["-s", 'testcases/test_ble.py'])    
        



