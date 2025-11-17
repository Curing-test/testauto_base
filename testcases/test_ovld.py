import os
import sys
import time
import pytest
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models import xiaoan_485_bus
from models.overload import Overload2
from models.externalPower import ExternalPower
from models import excel_report
from models.xiaoan_json import XiaoAnJson
from utils.aliyun_util import AliyunLog
from config import config


class OVLDTest:

    def setup_class(self):
        # 执行测试前，创建excel
        self.test_suit_name   = "OVLD测试"
        self.test_function    = "OVLD测试"
        self.start_time_str   = str(datetime.now())[0:19].replace(":", "-")
        self.report_file_name = os.path.join(config.EXCEL_REPORT_PATH, f"{config.DEVICE_TYPE_CHANGE}_v{config.devVsn}-{self.test_suit_name}报告_{self.start_time_str}.xlsx")
        self.imei             = config.IMEI
        self.excutor          = XiaoAnJson()
        self.external_power   = ExternalPower()
        xiaoan_485_bus.main()
        self.ovld             = xiaoan_485_bus.ovld
        self.motor_controller = xiaoan_485_bus.motor_controller
        self.aliyun_log = AliyunLog()
        excel_report.generator_header(file_name=self.report_file_name,sheet_name=self.test_function)
        """使能OVLD
        """        
        for _ in range(2):
            ret = self.excutor.c31()
            ovld_enable = ret['result.isOvldEnable']
            if not ovld_enable:
                self.excutor.c32(isOvldEnable=1)
                time.sleep(2)
            if ovld_enable:
                break
        ret = self.excutor.c31()
        assert ret['result.isOvldEnable'] == 1, f"OVLD使能失败，当前状态为{ret['result.isOvldEnable']}"


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
        self.ovld.loose_head()
        self.ovld.loose_tail()
        time.sleep(2)
        self.excutor.c4(defend = 1)

    def teardown_method(self):
        self.motor_controller.wheel_span_status = False
        self.motor_controller.speed             = 0

    def teardown_class(self):
        # 所有用例执行完成后，更新excel结果
        print("teardown_class")
        self.ovld.loose_head()
        self.ovld.loose_tail()

    def test_ovldType_0002_ovld_while_acc_on(self):
        self.description = "先超载后开电门 - 开电门超载"
        self.ovld.trig_head()
        self.ovld.trig_tail()
        time.sleep(3)
        ret = self.excutor.c33(acc=1,isOvld=2)
        assert ret['code'] == 142, f"开电门超载，返回码错误，返回码应为142，实际为{ret['code']}"
        log_list = self.aliyun_log.query_logs(past_time=15, query_string=self.imei, bin=5, log_type=55)
        assert len(log_list) > 0, f"开电门超载，云端日志查询失败"
        # TODO(bin.68日志解析)
        assert self.motor_controller.get_acc_status() == False, f"开电门超载，acc状态错误"
        ret = self.excutor.c34()
        assert ret['result.defend'] == 1, f"开电门超载，设防状态{ret['result.defend']}错误"
        assert ret['result.acc'] == 0, f"开电门超载，电门状态{ret['result.acc']}错误"
        self.ovld.loose_tail()
        log_list = self.aliyun_log.query_logs(past_time=20, query_string=self.imei, bin=5, log_type=56)
        assert len(log_list) > 0, f"开电门超载，云端日志查询失败"
        self.excutor.c33(acc=1,isOvld=2)
        time.sleep(2)
        ret = self.excutor.c34()
        assert ret['result.defend'] == 0, f"未超载状态下开电门，设防状态{ret['result.defend']}错误"
        assert self.motor_controller.get_acc_status() == True, f"未超载状态下开电门，acc状态错误"

    def test_ovldType_0003_ovld_restore(self):
        self.description = "先超载后开电门 - 超载恢复"
        ret = self.excutor.c33(acc=1,isOvld=2)
        assert ret['code'] == 0, f"未超载状态下开电门，返回码错误，返回码应为0，实际为{ret['code']}"
        assert self.motor_controller.get_acc_status() == True, f"未超载状态下开电门，acc状态错误"

    def test_ovldType_0004_triggle_ovld(self):
        self.description = "先开电门后超载 - 触发超载"
        ret = self.excutor.c33(acc=1,isOvld=2)
        assert ret['code'] == 0, f"未超载状态下开电门，返回码错误，返回码应为0，实际为{ret['code']}"
        assert self.motor_controller.get_acc_status() == True, f"未超载状态下开电门，acc状态错误"
        self.ovld.trig_head()
        self.ovld.trig_tail()
        time.sleep(3)
        assert self.motor_controller.get_acc_status() == False, f"超载状态下开电门，acc状态错误"
        log_list = self.aliyun_log.query_logs(past_time=20, query_string=self.imei, bin=5, log_type=55)
        assert len(log_list) > 0, f"开电门后超载，云端日志查询失败"
        # TODO(bin.68日志解析)
        self.ovld.loose_head()
        time.sleep(3)
        log_list = self.aliyun_log.query_logs(past_time=20, query_string=self.imei, bin=5, log_type=56)
        assert len(log_list) > 0, f"开电门超载，云端日志查询失败"
        assert self.motor_controller.get_acc_status() == True, f"超载后恢复未超载模式，acc状态错误"

    def test_ovldType_0005_reboot_remain(self):
        self.description = "先开电门后超载 - 重启保持"
        ret = self.excutor.c33(acc=1,isOvld=2)
        time.sleep(2)
        assert ret['code'] == 0, f"未超载状态下开电门，返回码错误，返回码应为0，实际为{ret['code']}"
        assert self.motor_controller.get_acc_status() == True, f"未超载状态下开电门，acc状态错误"
        self.ovld.trig_head()
        self.ovld.trig_tail()
        time.sleep(3)
        self.excutor.c21()
        time.sleep(30)
        log_list = self.aliyun_log.query_logs(past_time=35, query_string=self.imei, bin=5, log_type=55)
        assert len(log_list) > 0, f"超载后重启，云端日志查询失败"
        ret = self.excutor.c34()
        assert ret['result.defend'] == 0, f"重启后，设防状态{ret['result.defend']}错误"
        assert self.motor_controller.get_acc_status() == False, f"超载状态下重启，acc状态错误"

    def test_ovldType_0006_ovld_recover(self):
        self.description = "先开电门后超载 - 超载恢复"
        ret = self.excutor.c33(acc=1,isOvld=2)
        assert ret['code'] == 0, f"未超载状态下开电门，返回码错误，返回码应为0，实际为{ret['code']}"
        assert self.motor_controller.get_acc_status() == True, f"未超载状态下开电门，acc状态错误"

    def test_ovldType_0007_riding_ovld_less_than_10(self):
        self.description = "骑行超载 - 速度大于10不断电"
        ret = self.excutor.c33(acc=1,isOvld=2)
        self.motor_controller.speed = 11
        time.sleep(5)
        self.ovld.trig_head()
        self.ovld.trig_tail()   
        time.sleep(3)
        log_list = self.aliyun_log.query_logs(past_time=20, query_string=self.imei, bin=5, log_type=55)
        assert len(log_list) > 0, f"骑行超载，云端日志查询失败"
        # TODO(bin.68日志解析)
        assert self.motor_controller.get_acc_status() == True, f"骑行超载速度大于10，acc状态错误"

    def test_ovldType_0008_riding_ovld_greater_than_10(self):
        self.description = "骑行超载 - 速度小于等于10断电"
        ret = self.excutor.c33(acc=1,isOvld=2)
        self.motor_controller.speed = 10
        time.sleep(5)
        self.ovld.trig_head()
        self.ovld.trig_tail()   
        time.sleep(3)
        log_list = self.aliyun_log.query_logs(past_time=20, query_string=self.imei, bin=5, log_type=55)
        assert len(log_list) > 0, f"骑行超载，云端日志查询失败"
        # TODO(bin.68日志解析)
        assert self.motor_controller.get_acc_status() == False, f"骑行超载速度小于10，未断电"

    def test_ovldType_0009_no_person(self):
        self.description = "触点检测 - 无人检测"
        ret = self.excutor.c33(acc=1,isOvld=1)
        time.sleep(3)
        assert self.motor_controller.get_acc_status() == True, f"无人检测，acc状态错误"

    def test_ovldType_0010_one_person_front(self):
        self.description = "触点检测 - 一人前"
        self.ovld.trig_head()
        time.sleep(3)
        ret = self.excutor.c33(acc=1,isOvld=1)
        time.sleep(3)
        assert self.motor_controller.get_acc_status() == True, f"无人检测，acc状态错误"

    def test_ovldType_0011_one_person_tail(self):
        self.description = "触点检测 - 一人后"
        self.ovld.trig_tail()
        time.sleep(3)
        ret = self.excutor.c33(acc=1,isOvld=1)
        time.sleep(3)
        assert self.motor_controller.get_acc_status() == True, f"无人检测，acc状态错误"
    
    def test_ovldType_0012_two_person(self):
        self.description = "触点检测 - 二人前后"
        self.ovld.trig_head()
        self.ovld.trig_tail()
        time.sleep(3)
        ret = self.excutor.c33(acc=1,isOvld=1)
        assert ret['code'] == 142, f"多人检测，返回码错误，返回码应为142，实际为{ret['code']}"
        time.sleep(3)
        assert self.motor_controller.get_acc_status() == False, f"无人检测，acc状态错误"




if __name__ == '__main__':
    pytest.main(["-s", 'testcases/test_ovld.py'])
