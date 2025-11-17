
import os
import sys
import json
import time
import requests
sys.path.append(
    (os.path.abspath(os.path.join(os.path.dirname(__file__), './'))))
from utils.log_util import Logger
log = Logger(level='info')


class HttpClient:
    def request(self, url, data, headers=None, method='post', retry=3, timeout=20):
        """http请求
        Args:
            url (_type_): 
            data (_type_): 
            headers (_type_, optional): _description_. Defaults to None.
            method (str, optional): _description_. Defaults to 'post'.
            retry 
        Returns:
            _type_: 
        """
        if not headers:
            headers = {
                "Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
        for _ in range(retry):
            try:
                log.logger.info('http {} : {}'.format(method, json.dumps(data)))
                my_response = requests.request(
                    method=method, url=url, headers=headers, json=data,timeout=timeout)
                log.logger.info('http response : {}'.format(my_response.content.decode()))
                ret = {}
                if my_response.content:
                    ret = json.loads(my_response.content.decode())
                if 'code' in ret and ret.get('code', None) == 108:
                    log.logger.warning('通讯超时')
                    time.sleep(1)
                    continue
                if my_response.status_code:
                    return ret,  my_response.status_code
                return ret, -1
            except Exception as e:  # 抛出异常
                log.logger.error('http error : {}'.format(e))
        return {}, -1
