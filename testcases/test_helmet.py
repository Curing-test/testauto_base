#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   :   test_helmet.py
@Time   :   2025/01/25 19:07:24
@Author :   lee
@Version:   1.0
@Desc   :   None
"""


from datetime import datetime
import json
import os
import sys
import time
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models.helmetLock import HelmetLock6
from models.externalPower import ExternalPower
from models.xiaoan_json import XiaoAnJson
from config import config
from models import excel_report
from utils.aliyun_util import AliyunLog


class HelmetTest:
    TEST_ORDER = 0
    def setup_class(self):
        # 执行测试前，创建excel
        self.test_suit_name   = "头盔锁测试"
        self.test_function    = "功能测试"
        self.start_time_str   = str(datetime.now())[0:19].replace(":", "-")
        self.report_file_name = os.path.join(
            config.EXCEL_REPORT_PATH, f"{config.DEVICE_TYPE_CHANGE}_v{config.devVsn}-{self.test_suit_name}报告_{self.start_time_str}.xlsx")
        excel_report.generator_header(file_name=self.report_file_name,sheet_name=self.test_function)
        self.imei    = config.IMEI
        self.excutor = XiaoAnJson()
        self.aliyun_log = AliyunLog()
        self.helmet = HelmetLock6()
        self.externalPower = ExternalPower()

    def teardown_method(self):
        self.externalPower.connect()

    def test_helmetType_0007_unlock_helmet(self):
        self.description          = f"验证正常开锁"
        self.helmet.set_induction_state(True)
        self.helmet.set_unlock_state(False)
        assert self.helmet.check_unlock_state() == False, "头盔锁应上锁"
        assert self.helmet.check_induction_state() == True, "头盔锁应在位"
        self.excutor.c82(sw=0,isAutoLock=0)     # 解锁
        time.sleep(3)
        ret = self.excutor.c34()
        assert ret.get("result.helmet6Lock") == 0, "头盔锁应开锁"
        assert ret.get("result.helmet6React") == 1, "头盔锁应在位"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=44)
        assert len(log_list) >= 1, "应有bin5，type44上报"
        self.helmet.pickup_helmet()
        time.sleep(1)
        ret = self.excutor.c34()
        assert ret.get("result.helmet6Lock") == 0, "头盔锁应开锁"
        assert ret.get("result.helmet6React") == 0, "头盔锁应离位"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=41)
        assert len(log_list) >= 1, "应有bin5，type41上报"
        # TODO(bin.68解析)

    def  test_helmetType_0008_induction_auto_lock_after_unlock(self):
        self.description          = f"开锁有感应后自动上锁"
        self.helmet.set_induction_state(True)
        self.helmet.set_unlock_state(False)
        assert self.helmet.check_unlock_state() == False, "头盔锁应上锁"
        assert self.helmet.check_induction_state() == True, "头盔锁应在位"
        self.excutor.c82(sw=0,isAutoLock=1)     # 解锁
        time.sleep(3)
        self.helmet.pickup_helmet()
        time.sleep(1)
        self.helmet.restore_helmet()
        time.sleep(5)
        assert self.helmet.check_unlock_state() == False, "头盔应自动上锁"
        # TODO(语音校验)
        ret = self.excutor.c34()
        assert ret.get("result.helmet6Lock") == 1, "头盔锁应上锁"
        assert ret.get("result.helmet6React") == 1, "头盔锁应在位"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=43)
        assert len(log_list) >= 1, "应有bin5，type43上报"

    def  test_helmetType_0009_acc_on_to_unlock_helmet(self):
        self.description          = f"开电门关联解锁头盔"
        self.helmet.set_induction_state(True)
        self.helmet.set_unlock_state(False)
        assert self.helmet.check_unlock_state() == False, "头盔锁应上锁"
        assert self.helmet.check_induction_state() == True, "头盔锁应在位"
        self.excutor.c33(acc=1, helmetUnlock=1)
        time.sleep(5)
        ret = self.excutor.c34()
        assert ret.get("result.acc") == 1, "电门应开启"
        assert ret.get("result.helmet6Lock") == 0, "头盔锁应解锁"

    def test_helmetType_0010_not_auto_unlock_after_lock_fail(self):
        self.description          = f"上锁失败后不自动开锁"
        self.helmet.set_induction_state(False)
        self.helmet.set_unlock_state(True)
        assert self.helmet.check_unlock_state() == True, "头盔锁应解锁"
        assert self.helmet.check_induction_state() == False, "头盔锁应离位"
        time.sleep(2)
        self.excutor.c82(sw=1, isAutoOpen=0)
        time.sleep(5)
        ret = self.excutor.c34()
        assert ret.get("result.helmet6Lock") == 1, "头盔锁应上锁"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=47)
        assert len(log_list) >= 1, "应有bin5，type47上报"

    def test_helmetType_0011_auto_unlock_after_lock_fail(self):
        self.description          = f"上锁失败后自动开锁"
        self.helmet.set_induction_state(False)
        self.helmet.set_unlock_state(True)
        assert self.helmet.check_unlock_state() == True, "头盔锁应解锁"
        assert self.helmet.check_induction_state() == False, "头盔锁应离位"
        time.sleep(2)
        self.excutor.c82(sw=1, isAutoOpen=1)
        time.sleep(5)
        ret = self.excutor.c34()
        assert self.helmet.check_unlock_state() == True, "头盔锁应解锁"
        assert ret.get("result.helmet6Lock") == 0, "头盔锁应解锁"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=47)
        assert len(log_list) >= 1, "应有bin5，type47上报"

    def test_helmetType_0012_01_lock_cheating(self):
        self.description          = f"上锁欺骗1"
        self.helmet.set_induction_state(True)
        self.helmet.set_unlock_state(False)
        assert self.helmet.check_unlock_state() == False, "头盔锁应关锁"
        assert self.helmet.check_induction_state() == True, "头盔锁应在位"
        time.sleep(2)
        self.excutor.c82(sw=0, isAutoLock=1)
        time.sleep(5)
        ret = self.excutor.c34()
        assert self.helmet.check_unlock_state() == True, "头盔锁应解锁"
        assert ret.get("result.helmet6Lock") == 0, "头盔锁应解锁"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=44)
        assert len(log_list) >= 1, "应有bin5，type44上报"
        self.helmet.pickup_helmet()
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=41)
        assert len(log_list) >= 1, "应有bin5，type41上报"
        self.helmet.restore_helmet()
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=42)
        assert len(log_list) >= 1, "应有bin5，type42上报"
        time.sleep(5)
        assert self.helmet.check_unlock_state() == False, "头盔锁应上锁"
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=43)
        assert len(log_list) >= 1, "应有bin5，type43上报"

    def test_helmetType_0012_02_lock_cheating(self):
        self.description          = f"上锁欺骗2"
        self.helmet.set_induction_state(True)
        self.helmet.set_unlock_state(False)
        assert self.helmet.check_unlock_state() == False, "头盔锁应关锁"
        assert self.helmet.check_induction_state() == True, "头盔锁应在位"
        time.sleep(2)
        self.excutor.c82(sw=0, isAutoLock=1)
        time.sleep(5)
        ret = self.excutor.c34()
        assert self.helmet.check_unlock_state() == True, "头盔锁应解锁"
        assert ret.get("result.helmet6Lock") == 0, "头盔锁应解锁"
        self.helmet.pickup_helmet()
        time.sleep(2)
        self.helmet.restore_helmet()
        time.sleep(0.5)
        self.helmet.pickup_helmet()
        log_list = self.aliyun_log.query_logs(past_time=10, query_string=self.imei,bin=5,log_type=44)
        assert len(log_list) >= 1, "应有bin5，type44上报"   # pass
        for i in range(6):
            self.helmet.restore_helmet()
            time.sleep(0.5)
            self.helmet.pickup_helmet()
            time.sleep(2)   
        ret = self.excutor.c34()
        assert ret.get("result.helmet6Lock") == 0, "头盔锁应上锁"   # TODO(确认功能是否已移除)
        assert ret.get("result.helmet6React") == 0, "头盔锁应离位"

    def test_helmetType_0013_defend_to_lock_helmet(self):
        self.description          = f"设防关联上锁头盔"
        self.helmet.set_induction_state(True)
        self.helmet.set_unlock_state(True)
        assert self.helmet.check_unlock_state() == True, "头盔锁应开锁"
        assert self.helmet.check_induction_state() == True, "头盔锁应在位"
        self.excutor.c4(defend=1, isLockHelmet=1)
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret.get("result.defend") == 1, "车辆应设防"
        assert ret.get("result.helmet6Lock") == 1, "头盔锁应上锁"

if __name__ == "__main__":
    pytest.main(["-s", "testcases/test_helmet.py"])
