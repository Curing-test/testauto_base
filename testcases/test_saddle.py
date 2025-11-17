from datetime import datetime
import json
import os
import sys
import time
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models.externalPower import ExternalPower
from models.saddle import SaddleType1
from models.xiaoan_json import XiaoAnJson
from config import config
from models import excel_report
from utils.aliyun_util import AliyunLog


class SaddleTest:
    TEST_ORDER = 0
    def setup_class(self):
        # 执行测试前，创建excel
        self.test_suit_name   = "电池仓锁测试"
        self.test_function    = "功能测试"
        self.start_time_str   = str(datetime.now())[0:19].replace(":", "-")
        self.report_file_name = os.path.join(
            config.EXCEL_REPORT_PATH, f"{config.DEVICE_TYPE_CHANGE}_v{config.devVsn}-{self.test_suit_name}报告_{self.start_time_str}.xlsx")
        excel_report.generator_header(file_name=self.report_file_name,sheet_name=self.test_function)
        self.imei    = config.IMEI
        self.excutor = XiaoAnJson()
        self.aliyun_log = AliyunLog()
        self.saddle = SaddleType1()
        self.externalPower = ExternalPower()

    def teardown_method(self):
        self.externalPower.connect()


    def test_saddleType_0001_unlock_saddle(self):
        self.description          = f"开电池仓锁"
        self.saddle.lock()
        assert self.saddle.check_state() == 1, "电池仓锁应为关锁状态"
        self.excutor.c40(sw=0)
        time.sleep(3)
        assert self.saddle.check_state() == 0, "电池仓锁应为开锁状态"
        ret = self.excutor.c34()
        assert ret.get("result.seatLock") == 0, "seatLock应为0"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=9)
        assert len(log_list) >= 1, "应有bin5，type9上报"

    def test_saddleType_0002_lock_saddle(self):
        self.description          = f"关电池仓锁"
        self.saddle.unlock()
        assert self.saddle.check_state() == 0, "电池仓锁应开启"
        self.saddle.lock()
        assert self.saddle.check_state() == 1, "电池仓锁应为上锁状态"
        ret = self.excutor.c34()
        assert ret.get("result.seatLock") == 1, "seatLock应为1"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=10)
        assert len(log_list) >= 1, "应有bin5，type10上报"

    def test_saddleType_0003_restart_ECU_while_saddle_unlock(self):
        self.description          = f"电池仓未锁状态下重启设备"
        self.saddle.unlock()
        assert self.saddle.check_state() == 0, "电池仓锁应开启"
        self.saddle.set_reset_state(False)  # 配置复位状态为False
        self.excutor.c21()
        time.sleep(30)
        assert self.saddle.get_reset_state(), "电池仓锁应复位"
        ret = self.excutor.c34()
        assert ret.get("result.seatLock") == 0, "seatLock应为0"


    def test_saddleType_0004_restart_ECU_while_saddle_locked(self):
        self.description          = f"电池仓已锁状态下重启设备"
        self.saddle.lock()
        assert self.saddle.check_state() == 1, "电池仓锁应上锁"
        self.saddle.set_reset_state(False)  # 配置复位状态为False
        self.excutor.c21()
        time.sleep(30)
        assert self.saddle.get_reset_state()==False, "电池仓锁应无动作"
        ret = self.excutor.c34()
        assert ret.get("result.seatLock") == 1, "seatLock应为1"

    def test_saddleType_0005_disconnect_power_while_saddle_unlock(self):
        self.description          = f"电池仓未锁状态下断电"
        self.saddle.unlock()
        assert self.saddle.check_state() == 0, "电池仓锁应开启"
        self.saddle.set_reset_state(False)
        self.externalPower.disconnect()       # 断开大电
        time.sleep(1)
        self.externalPower.connect()          # 接通大电
        time.sleep(5)
        assert self.saddle.get_reset_state(), "电池仓锁应复位"
        ret = self.excutor.c34()
        assert ret.get("result.seatLock") == 0, "seatLock应为0"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=11)
        assert len(log_list) >= 1, "应有bin5，type11上报"

    def test_saddleType_0006_disconnect_power_while_saddle_locked(self):
        self.description          = f"电池仓已锁状态下断电"
        self.saddle.lock()
        assert self.saddle.check_state() == 1, "电池仓锁应上锁"
        self.saddle.set_reset_state(False)
        self.externalPower.disconnect()       # 断开大电
        time.sleep(3)
        assert self.saddle.get_reset_state()==False, "断大电，电池仓锁应不复位"
        self.externalPower.connect()          # 接通大电
        time.sleep(5)
        assert self.saddle.get_reset_state()==True, "接大电，电池仓锁应复位"
        ret = self.excutor.c34()
        assert ret.get("result.seatLock") == 1, "seatLock应为1"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=11)
        assert len(log_list) >= 1, "应有bin5，type11上报"


    def test_saddleType_0007_unlock_saddle_use_battery(self):
        self.description          = f"小电池开关电池仓"
        self.saddle.lock()
        assert self.saddle.check_state() == 1, "电池仓锁应上锁"
        self.externalPower.disconnect()       # 断开大电
        time.sleep(1)
        self.excutor.c40(sw=0)
        time.sleep(3)
        assert self.saddle.check_state()==0,"电池仓锁应解锁"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=9)
        assert len(log_list) >= 1, "应有bin5，type9上报"
        self.saddle.lock()
        assert self.saddle.check_state()==1,"电池仓锁应上锁"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=10)
        assert len(log_list) >= 1, "应有bin5，type10上报"

if __name__ == '__main__':
    pytest.main(["-s", "testcases/test_saddle.py"])