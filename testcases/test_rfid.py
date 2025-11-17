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


class RFIDTest:
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
        self.rfid             = xiaoan_485_bus.rfid
        self.rfid.card_id     = "BB"*8
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
        self.excutor.c4(defend = 1)

    def teardown_method(self):
        self.motor_controller.wheel_span_status = False
        self.motor_controller.speed             = 0

    def teardown_class(self):
        # 所有用例执行完成后，更新excel结果
        print("teardown_class")

    def test_isRFIDEnable_0001_RFID_state(self): 
        self.description = "RFID状态1 "
        self.rfid.connect()
        self.excutor.c33(acc = 1)
        time.sleep(10)
        self.rfid.set_card(self.rfid.card_id)
        time.sleep(5)
        ret = self.excutor.c34()
        assert ret['result.RFID.event'] == 1
        assert ret['result.RFID.cardID'] == self.rfid.card_id

    def test_isRFIDEnable_0002_RFID_state(self):
        self.description = "RFID状态0"
        self.rfid.connect()
        self.excutor.c33(acc = 1)
        time.sleep(10)
        self.rfid.set_card(self.rfid.card_id)
        time.sleep(5)
        ret = self.excutor.c34()
        assert ret['result.RFID.event'] == 1
        assert ret['result.RFID.cardID'] == self.rfid.card_id
        self.rfid.pick_up_card()
        time.sleep(5)
        self.motor_controller.wheel_span_status = True
        self.motor_controller.speed = 4
        time.sleep(60 + 5)
        ret = self.excutor.c34()
        assert ret['result.RFID.event'] == 0
        assert 'result.RFID.cardID' not in ret

    def test_isRFIDEnable_0003_RFID_state(self):
        self.description = "RFID状态3"
        self.rfid.connect()
        time.sleep(5)
        self.rfid.set_card(self.rfid.card_id)
        time.sleep(5)
        self.motor_controller.wheel_span_status = True
        time.sleep(5)
        ret = self.excutor.c34()
        assert ret['result.RFID.event'] == 3
        # TODO(语音播报校验)

    def test_isRFIDEnable_0004_RFID_state(self):
        self.description = "RFID状态"
        self.excutor.c33(acc = 1)
        time.sleep(3)
        self.excutor.c33(acc = 0)
        self.rfid.connect()
        self.rfid.set_card(self.rfid.card_id)
        time.sleep(20)
        ret = self.excutor.c34()
        assert ret['result.RFID.event'] == 1
        assert ret['result.RFID.cardID'] == self.rfid.card_id
        self.rfid.pick_up_card()
        time.sleep(5)
        # self.motor_controller.wheel_span_status = True
        # self.motor_controller.speed = 5
        time.sleep(60)
        ret = self.excutor.c34()
        assert ret['result.RFID.event'] == 0
        assert 'result.RFID.cardID' not in ret

    def test_isRFIDEnable_0005_RFID_state(self):
        self.description = "RFID状态"
        self.external_power.disconnect()
        self.excutor.c33(acc = 1)
        time.sleep(3)
        self.rfid.connect()
        self.rfid.set_card(self.rfid.card_id)
        time.sleep(20)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 141
        ret = self.excutor.c34()
        assert ret['result.RFID.event'] == 3
        assert self.rfid.acc_status == False

    def test_isRFIDEnable_0006_RFID_restore_car(self):
        tlv_RFID = False
        self.description = "RFID还车"
        self.excutor.c33(acc = 1)
        time.sleep(3)
        self.rfid.connect()
        self.rfid.set_card(self.rfid.card_id)
        time.sleep(20)
        self.aliyun_log.query_logs(past_time=15, query_string=self.imei, bin=68)
        # TODO(bin.68协议解析)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret.get("result.RFID.event") ==1
        assert ret.get("result.RFID.id") == self.rfid.card_id

    def test_isRFIDEnable_0007_RFID_restore_car(self):
        self.description = "RFID还车"
        self.excutor.c33(acc = 1)
        time.sleep(3)
        self.rfid.connect()
        time.sleep(20)
        self.aliyun_log.query_logs(past_time=15, query_string=self.imei, bin=68)
        # TODO(bin.68协议解析)
        self.motor_controller.wheel_span_status = True
        self.motor_controller.speed = 0
        time.sleep(10)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 0
        time.sleep(60)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 0

    def test_isRFIDEnable_0008_RFID_restore_car(self):
        self.description = "RFID还车"
        self.excutor.c33(acc = 1)
        time.sleep(3)
        self.rfid.disconnect()
        time.sleep(20)
        self.aliyun_log.query_logs(past_time=15, query_string=self.imei, bin=68)
        # TODO(bin.68协议解析)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 136
        assert ret['result.RFID.event'] == 0

    def test_isRFIDEnable_0009_RFID_restore_car(self):
        self.description = "RFID还车"
        self.excutor.c33(acc = 0)
        time.sleep(3)
        self.rfid.connect()
        self.rfid.set_card(self.rfid.card_id)
        time.sleep(20)
        self.aliyun_log.query_logs(past_time=15, query_string=self.imei, bin=68)
        # TODO(bin.68协议解析)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 0
        # assert ret['result.RFID.event'] == 1

    def test_isRFIDEnable_0010_RFID_restore_car(self):
        self.description = "RFID还车"
        self.excutor.c33(acc = 0)
        time.sleep(3)
        self.rfid.connect()
        self.rfid.pick_up_card()
        time.sleep(20)
        # self.aliyun_log.query_logs(past_time=15, query_string=self.imei, bin=68)
        # TODO(bin.68协议解析)
        self.motor_controller.wheel_span_status = True
        time.sleep(10)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 136
        time.sleep(60)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 136

    def test_isRFIDEnable_0011_RFID_restore_car(self):
        self.description = "RFID还车"
        self.excutor.c33(acc = 0)
        time.sleep(3)
        self.rfid.disconnect()
        time.sleep(20)
        self.aliyun_log.query_logs(past_time=15, query_string=self.imei, bin=68)
        # TODO(bin.68协议解析)
        self.motor_controller.wheel_span_status = True
        time.sleep(10)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 136
        time.sleep(60)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 136

    def test_isRFIDEnable_0012_RFID_restore_car(self):
        self.description = "RFID还车"
        self.excutor.c33(acc = 0)
        time.sleep(3)
        self.rfid.connect()
        time.sleep(20)
        # self.aliyun_log.query_logs(past_time=15, query_string=self.imei, bin=68)
        # TODO(bin.68协议解析)
        time.sleep(10)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 136
        time.sleep(60)
        ret = self.excutor.c4(defend=1, isRFID=1)
        assert ret['code'] == 136

if __name__ == '__main__':
    pytest.main(["-s", 'testcases/test_rfid.py::RFIDTest::test_isRFIDEnable_0012_RFID_restore_car']) #
    # pytest.main(["-s", 'testcases/test_rfid.py'])