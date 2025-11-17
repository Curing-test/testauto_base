import json
import os
import sys
# import time
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.http_util import HttpClient
from utils.aliyun_util import AliyunLog
from utils.log_util import Logger
log = Logger(level='info')


def flatten_dict(d, parent_key='', sep='.'):
    """将字典展开，保留原始 JSON 的层级结构

    Args:
        d (dict): 要展开的字典
        parent_key (str): 父键名，用于递归时构建新的键名
        sep (str): 分隔符，用于分隔不同层级的键名

    Returns:
        dict: 展开后的字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class XiaoAnProtocol:

    def __init__(self):
        self.http_client = HttpClient()
        self.aliyun_log = AliyunLog()

    def send_request(self, url, payload, method='post', flatten=True, timeout=10):
        ret, _  = self.http_client.request(url, payload, method=method, timeout=timeout)
        if flatten:
            return flatten_dict(ret)
        return ret

    def handle(self, url, payload, method='post', resp_check_type=None,expect_resp={}, past_time=10, query_string='', bin=None, log_type=None, bin_report=False, retry=3, timeout=10):
        """_summary_
        Args:
            url (_type_): _description_
            payload (_type_): _description_
            method (str, optional): _description_. Defaults to 'post'.
            expect_resp (dict, optional): _description_. Defaults to {}.
            past_time (int, optional): _description_. Defaults to 0.
            query_string (str, optional): _description_. Defaults to ''.
            bin (_type_, optional): _description_. Defaults to None.
            log_type (_type_, optional): _description_. Defaults to None.
            bin_report (bool, optional): 不上报. Defaults to False.
            retry (int, optional): _description_. Defaults to 3.
        Returns:
            _type_: _description_
        """
        http_result, http_ret, status_code, log_report = False,"", "", ""
        for _ in range(retry):
            # http请求
            http_ret, status_code = self.http_client.request(url=url, data=payload, method=method, retry=retry, timeout=timeout)
            if status_code == -1:
                continue
            http_result = self.check_http_result(resp_check_type, http_ret, expect_resp=expect_resp)
            if not http_result:
                return False, http_ret, status_code, log_report
            # 无需上报
            if not bin:
                return True, http_ret, status_code, log_report
            log_result = self.aliyun_log.query_logs(past_time, query_string, bin, log_type)
            if bin_report == "上报" and len(log_result) > 0:
                # 需要上报而且上报了
                return True, http_ret, status_code, log_result
            if bin_report == "不上报" and len(log_result) == 0:
                # 不上报而且没有上报
                return True, http_ret, status_code, log_result
        return http_result, http_ret, status_code, log_report

    def check_http_result(self, resp_check_type, ret, expect_resp):
        if isinstance(expect_resp, dict):
            if resp_check_type == "C18":
                return expect_resp in ret.get("result").get("deviceTypes")
            flat_ret = flatten_dict(ret)
            if resp_check_type == "C9":
                result = ret.get("result")[0]
                flat_ret = flatten_dict(result)
            if resp_check_type == "不存在":
                for k in expect_resp.keys():
                    if expect_resp.get(k) == flat_ret.get(k):
                        log.logger.info(f"预期不存在{k}: {expect_resp.get(k)}，实际存在")
                        return False
                return True
            for k in expect_resp.keys():
                if expect_resp.get(k) != flat_ret.get(k):
                    log.logger.info(f"预期存在{k}: {expect_resp.get(k)}，实际为{flat_ret.get(k)}")
                    return False
            return True
        elif isinstance(expect_resp, list):
            flat_ret = flatten_dict(ret)
            for k in expect_resp:
                if k not in flat_ret.keys():
                    return False
        else:
            log.logger.error("expect_resp 类型错误")
        return True


if __name__ == "__main__":
    a = XiaoAnProtocol()
    ret = {  "code": 0,  "result": {    "IMSI": "460042185912368",    "CCID": "89860401102240067868"}  }
    print(a.check_http_result(resp_check_type=None,ret= ret,expect_resp=["result.IMSI", "result.CCID"]))
    # dd = {"code":0,"result":{"server":"112.74.77.182:9880"}}
    print(flatten_dict(ret))
