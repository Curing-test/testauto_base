from datetime import datetime
import json
import os
import sys
import time
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models.xiaoan_protocol import XiaoAnProtocol
from config import config
from models import excel_report, read_excel
from utils.aliyun_util import AliyunOss
from utils.crc16tool import calculate_crc16_file


class ProtocolTest:
    TEST_ORDER = 0
    def setup_class(self):
        # 执行测试前，创建excel
        self.test_suit_name   = "基本功能测试"
        self.test_function    = "接口测试"
        self.start_time_str   = str(datetime.now())[0:19].replace(":", "-")
        self.report_file_name = os.path.join(
            config.EXCEL_REPORT_PATH, f"{config.DEVICE_TYPE_CHANGE}_v{config.devVsn}-{self.test_suit_name}报告_{self.start_time_str}.xlsx")
        excel_report.generator_header(file_name=self.report_file_name,sheet_name=self.test_function)
        self.imei    = config.IMEI
        self.excutor = XiaoAnProtocol()
        self.c31_content = self.excutor.send_request(config.BASE_URL, {"imei": self.imei, "async": 'false', "cmd": {"c": 31, "param": {}}},flatten=False).get("result")

    def setup_method(self):
        # 每个用例执行前，初始化参数
        ProtocolTest.TEST_ORDER += 1
        self.order               = str(ProtocolTest.TEST_ORDER)
        self.description         = ""
        self.url                 = ""
        self.method              = "POST"
        self.time_str            = str(datetime.now())[0:19].replace(":", "-")
        self.expect_resp_http    = {}
        self.expect_resp         = ""
        self.status_code         = 0
        self.past_time           = 15
        self.resp                = {}
        self.resp_check_type     = None
        self.log_report          = ""
        self.result              = "fail"
        self.bin                 = None
        self.log_type            = None
        self.bin_report          = False
        self.wait_time           = 0
        self.payload             = {
                                "imei": self.imei,
                                "async": 'false',
                                "cmd"  : {
                                    "c"    : 0,
                                    "param": {
                                    }
                                }
                            }

    def teardown_method(self):
        excel_report.write_line(file_name=self.report_file_name,
                                sheet_name=self.test_function,
                                line=[{"content":self.order},
                                    {"content": self.description},
                                    {"content": self.url},
                                    {"content": self.method},
                                    {"content": self.time_str},
                                    {"content": json.dumps(self.payload)},
                                    {"content": self.expect_resp},
                                    {"content": self.status_code},
                                    {"content": json.dumps(self.resp)},
                                    {"content": str(self.log_report)},
                                    {"content": "pass" if self.result else "fail"},
                                    ])

    def teardown_class(self):
        # 所有用例执行完成后，更新excel结果
        print("teardown_class")
        self.excutor.send_request(config.BASE_URL, {"imei": self.imei, "async": 'false', "cmd": {"c": 32, "param": self.c31_content}},flatten=False)

    # @pytest.mark.skipif(config.SKIP_UPGRADE, reason="配置无需执行")
    @ pytest.mark.run(order=1)
    def test_protocol_type_regist_C18(self):
        command                   = 18
        self.description          = f"C18-查询服务器设备型号注册"
        self.url                  = config.MANGGUO_URL
        self.bin                  = None
        self.log_type             = None
        self.bin_report           = False
        self.payload['cmd']['c']  = command
        self.expect_resp_http     = config.DEVICE_TYPE_PARAM
        self.resp_check_type      = "C18"
        self.expect_resp          = str(self.resp_check_type) + str(self.expect_resp_http) + "\n" + str({"bin": self.bin, "type": self.log_type}) if self.bin else str(self.expect_resp_http)
        self.result, self.resp, self.status_code, self.log_report = self.excutor.handle(self.url, self.payload, method=self.method, resp_check_type=self.resp_check_type,
                                   expect_resp=self.expect_resp_http, past_time=self.past_time, query_string=config.IMEI, 
                                   bin=self.bin, log_type=self.log_type, bin_report=self.bin_report, retry=3,timeout=20)
        assert self.result

    @pytest.mark.skipif(config.SKIP_UPGRADE, reason="配置无需执行")
    @ pytest.mark.run(order=2)
    def test_protocol_type_config_C14(self):
        command                   = 14
        self.description          = f"C14-配置设备型号: {config.DEVICE_TYPE_CHANGE_NO_SUFFIX}"
        self.url                  = "http://ecu4cloud.xiaoantech.com/v1/server" #config.MANGGUO_URL # TODO(芒果大概需要80s响应)
        self.bin                  = None
        self.log_type             = None
        self.bin_report           = False
        self.resp_check_type      = None
        self.payload['cmd']['c']  = command
        self.payload['cmd']['param']['deviceType'] = config.DEVICE_TYPE_CHANGE_NO_SUFFIX
        self.payload['cmd']['param']['imeis'] = [self.imei]
        self.expect_resp_http     = {'code': 0}
        self.expect_resp          = str(self.expect_resp_http) + "\n" + str({"bin": self.bin, "type": self.log_type}) if self.bin else str(self.expect_resp_http)
        self.result, self.resp, self.status_code, self.log_report = self.excutor.handle(self.url, self.payload, method=self.method, resp_check_type=self.resp_check_type,
                                   expect_resp=self.expect_resp_http, past_time=self.past_time, query_string=config.IMEI, 
                                   bin=self.bin, log_type=self.log_type, bin_report=self.bin_report, retry=3, timeout=10)
        assert self.result

    @pytest.mark.skipif(config.SKIP_UPGRADE, reason="配置无需执行")
    @pytest.mark.run(order=3)
    def test_protocol_ota_update_C35(self):
        upgrade_pack_crc = calculate_crc16_file(config.upgrade_pack_file)
        aliyun_oss       = AliyunOss()
        oss_url          = aliyun_oss.put(config.upgrade_pack, config.upgrade_pack_file)
        command          = 35
        self.description = f"C35-OTA升级设备版本: {config.devVsn}"
        self.url                  = config.BASE_URL
        self.bin                  = None
        self.log_type             = None
        self.resp_check_type      = None
        self.bin_report           = False
        self.payload['cmd']['c']  = command
        self.payload['cmd']['param']["url"] = oss_url
        self.payload['cmd']['param']["crc"] = upgrade_pack_crc
        self.expect_resp_http     = {'code' : 0}
        self.expect_resp          = str(self.expect_resp_http) + "\n" + str({"bin": self.bin, "type": self.log_type}) if self.bin else str(self.expect_resp_http)
        self.result, self.resp, self.status_code, self.log_report = self.excutor.handle(self.url, self.payload, method=self.method, resp_check_type=self.resp_check_type,
                                   expect_resp=self.expect_resp_http, past_time=self.past_time, query_string=config.IMEI, 
                                   bin=self.bin, log_type=self.log_type, bin_report=self.bin_report, retry=3)
        time.sleep(config.UPGRADE_TIME)
        assert self.result



    @pytest.mark.parametrize("data", read_excel.read_excel_to_dict())
    def test_protocol_json_test(self, data):
        self.description      = data.get("description")
        self.url              = data.get("URL")
        self.bin              = int(data.get("bin")) if data.get("bin") else None
        self.log_type         = int(data.get("log_type")) if data.get("log_type") else None
        self.bin_report       = data.get("log_report") 
        self.resp_check_type  = data.get("resp_check_type")
        self.payload          = json.loads(data.get("payload"))
        self.expect_resp_http = json.loads(data.get("http_resp"))
        self.wait_time        = int(data.get("wait_time")) if data.get("wait_time") else 0
        self.expect_resp      = str(self.expect_resp_http) + "\n" + str(self.bin_report) + str({"bin": self.bin, "type": self.log_type}) if self.bin else str(self.expect_resp_http)
        self.result, self.resp, self.status_code, self.log_report = self.excutor.handle(self.url, self.payload, method=self.method, resp_check_type=self.resp_check_type,
                                   expect_resp=self.expect_resp_http, past_time=self.past_time, query_string=config.IMEI, 
                                   bin=self.bin, log_type=self.log_type, bin_report=self.bin_report, retry=3)
        if self.wait_time:
            time.sleep(self.wait_time)
        assert self.result

if __name__ == "__main__":
    pytest.main(["-s","testcases/test_json_protocol.py::ProtocolTest::test_protocol_type_regist_C18"])
