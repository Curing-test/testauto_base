from datetime import datetime
import os
import sys
import time
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models.bms import XingHengBMS
from models.externalPower import ExternalPower
from utils.aliyun_util import AliyunLog
from models import excel_report, read_excel, xiaoan_485_bus
from models.xiaoan_json import XiaoAnJson
from config import config


class BMSTest:
    def setup_class(self):
        # 执行测试前，创建excel
        self.test_suit_name   = "BMS测试"
        self.test_function    = "BMS测试"
        self.start_time_str   = str(datetime.now())[0:19].replace(":", "-")
        self.report_file_name = os.path.join( config.EXCEL_REPORT_PATH, f"{config.DEVICE_TYPE_CHANGE}_v{config.devVsn}-{self.test_suit_name}报告_{self.start_time_str}.xlsx")
        self.imei             = config.IMEI
        self.excutor          = XiaoAnJson()
        xiaoan_485_bus.main()
        self.BMS              = xiaoan_485_bus.bms
        self.external_power   = ExternalPower(bms=self.BMS)
        self.motor_controller = xiaoan_485_bus.motor_controller
        self.aliyun_log       = AliyunLog()
        excel_report.generator_header(file_name=self.report_file_name,sheet_name=self.test_function)

    def setup_method(self):
        # 每个用例执行前，初始化参数
        self.url         = ""
        self.description = ""
        self.method      = "POST"
        self.wait_time   = 0
        self.payload     = {
                                "imei" : self.imei,
                                "async": 'false',
                                "cmd"  : {
                                    "c"    : 0,
                                    "param": {
                                    }
                                }
                            }
        self.excutor.c4(defend = 1) # 设防

    def teardown_method(self):
        self.external_power.connect()

    def teardown_class(self):
        # 所有用例执行完成后，更新excel结果
        print("teardown_class")

    def test_bmsType_0021_0027(self): 
        self.description = "验证bmsType 1接大电状态"
        self.external_power.connect()
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret['result.BmsComm'] == 1, ""
        assert ret['result.powerState'] == 1, f"大电上电，powerState异常，应为1，实际值：{ret['result.powerState']}"
        self.excutor.c33(acc=1) # 开电门
        time.sleep(2)
        # TODO(bin.66,bin.68数据上报)
        ret = self.excutor.c34()
        assert ret['result.BmsComm'] == 1, ""
        assert ret['result.powerState'] == 1, f"大电上电，powerState异常，应为1，实际值：{ret['result.powerState']}"
        self.motor_controller.speed = 10
        time.sleep(5)
        assert ret['result.BmsComm'] == 1, ""
        assert ret['result.powerState'] == 1, f"大电上电，powerState异常，应为1，实际值：{ret['result.powerState']}"

    def test_bmsType_0028_0029(self):
        self.description = "验证bmsType:1未接大电状态"
        self.external_power.disconnect()
        time.sleep(2)
        # TODO(bin.66,bin.68数据上报)
        ret = self.excutor.c34()
        assert ret['result.BmsComm'] == 0, ""
        assert ret['result.powerState'] == 0, f"大电断开，powerState异常，应为0，实际值：{ret['result.powerState']}"

    def test_bmsType_0030_0035(self):
        self.description = "验证bmsType: 1 接大电换电"
        self.external_power.connect()
        time.sleep(2)
        self.external_power.disconnect()
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret['result.voltage'] == 0, f"断大电后电压应为0，实际值：{ret['result.voltage']}"
        assert ret['result.voltageMv'] == 0, f"断大电后电压应为0，实际值：{ret['result.voltageMv']}"
        assert ret['result.BmsComm'] == 0, ""
        assert ret['result.powerState'] == 0, f"大电离位，powerState异常，应为0，实际值：{ret['result.powerState']}"
        # TODO(bin.66,bin.68数据上报)
        self.BMS.sn = "xiaoan-fake-bms4"
        time.sleep(3)
        self.external_power.connect()
        time.sleep(5)
        ret = self.excutor.c34()
        assert ret['result.BmsComm'] == 1, f"大电在位，BMSComm异常，应为1，实际值为：{ret['result.BmsComm']}"
        assert ret['result.powerState'] == 1, f"大电上电，powerState异常，应为1，实际值：{ret['result.powerState']}"

    def test_bmsType_0036_0041(self):
        self.description = "验证bmsType: 1未接大电换电"
        self.external_power.disconnect()
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret['result.voltage'] == 0, f"断大电后电压应为0，实际值：{ret['result.voltage']}"
        assert ret['result.voltageMv'] == 0, f"断大电后电压应为0，实际值：{ret['result.voltageMv']}"
        assert ret['result.BmsComm'] == 0, ""
        assert ret['result.powerState'] == 0, f"大电离位，powerState异常，应为0，实际值：{ret['result.powerState']}"
        # TODO(bin.66,bin.68数据上报)
        self.BMS.sn = "xiaoan-fake-bms4"
        time.sleep(3)
        self.external_power.connect()
        time.sleep(5)
        ret = self.excutor.c34()
        assert ret['result.BmsComm'] == 1, f"大电在位，BMSComm异常，应为1，实际值为：{ret['result.BmsComm']}"
        assert ret['result.powerState'] == 1, f"大电上电，powerState异常，应为1，实际值：{ret['result.powerState']}"

    
        


if __name__ == '__main__':
    pytest.main(["-s", 'testcases/test_bms.py'])