#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   test_motor_controller.py
@Time   :   2025/04/20 10:31:49
@Author :   lee
@Version:   1.0
@Desc   :   控制器相关操作自动化测试用例
"""
from datetime import datetime
import os
import sys
import time
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models import xiaoan_485_bus
from models.externalPower import ExternalPower
from models import excel_report, read_excel
from models.xiaoan_json import XiaoAnJson
from utils.aliyun_util import AliyunLog
from config import config


class ETCTest:
    def setup_class(self):
        # 执行测试前，创建excel
        self.test_suit_name   = "RFID测试"
        self.test_function    = "RFID测试"
        self.start_time_str   = str(datetime.now())[0:19].replace(":", "-")
        self.report_file_name = os.path.join(config.EXCEL_REPORT_PATH, f"{config.DEVICE_TYPE_CHANGE}_v{config.devVsn}-{self.test_suit_name}报告_{self.start_time_str}.xlsx")
        self.imei             = config.IMEI
        self.excutor          = XiaoAnJson()
        self.external_power   = ExternalPower()
        xiaoan_485_bus.main()
        self.motor_controller = xiaoan_485_bus.motor_controller
        self.aliyun_log = AliyunLog()
        excel_report.generator_header(file_name=self.report_file_name,sheet_name=self.test_function)

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
        self.external_power.connect()
        self.motor_controller.wheel_span_status = False
        self.motor_controller.speed             = 0
        self.excutor.c4(defend = 1)
        time.sleep(1)

    def teardown_method(self):
        self.motor_controller.wheel_span_status = False
        self.motor_controller.speed             = 0

    def teardown_class(self):
        # 所有用例执行完成后，更新excel结果
        print("teardown_class")

    def test_ETCType_0001_acc_on_while_acc_off(self): 
        self.description = "关电门撤防状态下开电门 "
        self.excutor.c4(defend = 0)# 撤防
        ret = self.excutor.c34()
        assert ret.get("result.acc") == 0, "电门应处于关电门状态"
        assert ret.get("result.defend") == 0, "应处于撤防状态"
        self.excutor.c33(acc=1)     # 开电门
        time.sleep(3)
        assert self.motor_controller.acc_status == True, " 电门应处于开电门状态"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=7)
        assert len(log_list) >= 1, "关电门撤防状态下开电门，应有bin5，type7上报"

    def test_ETCType_0002_acc_on_while_defend(self): 
        self.description = "设防状态下开电门 "
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret.get("result.acc") == 0, "电门应处于关电门状态"
        assert ret.get("result.defend") == 1, "应处于设防状态"
        self.excutor.c33(acc=1)     # 开电门
        time.sleep(3)
        assert self.motor_controller.acc_status == True, " 电门应处于开电门状态"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=7)
        assert len(log_list) >= 1, "设防状态下开电门，应有bin5，type7上报"

    def test_ETCType_0003_acc_on_while_acc_on(self): 
        self.description = "开电门状态下开电门 "
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret.get("result.acc") == 0, "电门应处于关电门状态"
        assert ret.get("result.defend") == 1, "应处于设防状态"
        self.excutor.c33(acc=1)     # 开电门
        time.sleep(3)
        assert self.motor_controller.acc_status == True, " 电门应处于开电门状态"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=7)
        assert len(log_list) >= 1, "设防状态下开电门，应有bin5，type7上报"
        time.sleep(10)
        self.excutor.c33(acc=1)     # 开电门
        time.sleep(3)
        assert self.motor_controller.acc_status == True, " 电门应处于开电门状态"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=7)
        assert len(log_list) == 0, "开电门状态下开电门，应无bin5，type7上报"

    def test_ETCType_0004_acc_on_while_wheel_locked(self): 
        self.description = "后轮抱死状态下开电门"
        time.sleep(2)
        self.motor_controller.wheel_span_status = True
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret.get("result.acc") == 1, "电门应处于关电门状态"
        assert ret.get("result.defend") == 1, "应处于设防状态"
        assert self.motor_controller.defend_status == True, "后轮应处于抱死状态"
        self.excutor.c33(acc=1)     # 开电门
        time.sleep(3)
        assert self.motor_controller.acc_status == True, " 电门应处于开电门状态"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=7)
        assert len(log_list) >= 1, "抱死状态下开电门，应有bin5，type7上报"
        

    def test_ETCType_0005_acc_on_while_riding(self): 
        self.description = "骑行开电门"
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret.get("result.acc") == 0, "电门应处于开电门状态"
        assert ret.get("result.defend") == 1, "应处于设防状态"
        self.excutor.c33(acc=1)     # 开电门
        time.sleep(3)
        assert self.motor_controller.acc_status == True, " 电门应处于开电门状态"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=7)
        assert len(log_list) >= 1, "骑行状态下开电门，应有bin5，type7上报"

    def test_ETCType_0006_acc_off_while_acc_on(self): 
        self.description = "车辆静止，电门开启状态下开电门"
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret.get("result.acc") == 0, "电门应处于关电门状态"
        assert ret.get("result.defend") == 1, "应处于设防状态"
        self.excutor.c33(acc=1)     # 开电门
        time.sleep(3)
        assert self.motor_controller.acc_status == True, " 电门应处于开电门状态"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=7)
        assert len(log_list) >= 1, "设防状态下开电门，应有bin5，type7上报"
        self.motor_controller.speed = 10
        self.motor_controller.wheel_span_status = True
        time.sleep(10)
        self.excutor.c33(acc=1)     # 开电门
        time.sleep(3)
        assert self.motor_controller.acc_status == True, " 电门应处于开电门状态"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=7)
        assert len(log_list) == 0, "骑行开电门，应无bin5，type7上报"
    

if __name__ == "__main__":
    # pytest.main(["-s", "testcases/test_motor_controller.py"])
     pytest.main(["-s", "testcases/test_motor_controller.py::ETCTest::test_ETCType_0001_acc_on_while_acc_off"])
    # pytest.main(["-s", "testcases/test_motor_controller.py::ETCTest::test_ETCType_0002_acc_on_while_defend"])
    # pytest.main(["-s", "testcases/test_motor_controller.py::ETCTest::test_ETCType_0003_acc_on_while_acc_on"])
    # pytest.main(["-s", "testcases/test_motor_controller.py::ETCTest::test_ETCType_0004_acc_on_while_wheel_locked"])
    # pytest.main(["-s", "testcases/test_motor_controller.py::ETCTest::test_ETCType_0005_acc_on_while_riding"])