
from aliyun.log import LogClient, GetLogsRequest
import os
import sys
import time
import json
import re
import traceback
import oss2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from config import config
from utils.log_util import Logger
from utils.bin_util import BIN_api

logger = Logger(level='info').logger


class AliyunLog(object):
    def __init__(self, server=None, endpoint=None, project_name=None, logstore_name=None, access_key=None, access_keyID=None):
        self.server        = server or config.ALIYUN_SERVER
        self.endpoint      = endpoint or config.ALIYUN_LOG_ENDPOINT
        self.project_name  = project_name or config.ALIYUN_LOG_PROJECT
        self.logstore_name = logstore_name or config.ALIYUN_LOG_LOGSTORE
        self.access_key    = access_key or config.ALIYUN_LOG_ACCESSKEY
        self.access_keyID  = access_keyID or config.ALIYUN_LOG_ACCESSKEYID
        self.client        = LogClient(endpoint=self.endpoint, accessKey=self.access_key, accessKeyId=self.access_keyID)
        self.log_list      = list()
        self.bin_api       = BIN_api()

    def query_logs(self, past_time: int, query_string: str, bin=-1, log_type=-1):
        """根据查询语句查询当前时间前{past_time}s内的指定日志信息
        Args:
            past_time (int): _description_
            query_string (str): _description_
            bin:
            log_type:
        Returns:
            _type_: _description_
        """
        self.log_list = list()
        time.sleep(5)
        end_time = int(time.time())
        start_time = end_time - past_time - 5
        try:
            for _ in range(5):
                request = GetLogsRequest(self.project_name, self.logstore_name,
                                        start_time, end_time, query=query_string, line=10000)  # 暂定最大筛选1万条
                response = self.client.get_logs(request)
                logs = response.get_body().get("data")
                for log in logs:
                    # 去重
                    if log in self.log_list:
                        continue
                    lastBuff, bin_in_log, type_in_log = self.extract_info_from_log(log.get("content"))
                    # print(lastBuff, bin_in_log, type_in_log)
                    if int(bin) == int(bin_in_log) and int(log_type) == int(type_in_log):
                        self.log_list.append(log)       # 单条日志去重后添加到list
                logger.info(f"query: {query_string},bin: {bin},type: {log_type}, resp is: {str(self.log_list)}")
                if len(self.log_list) == 0:
                    time.sleep(5)
                    start_time = end_time
                    end_time = int(time.time())
                else:
                    break
        except Exception:
            logger.error(traceback.format_exc())
        return self.log_list
    
    def parse_logs(self):
        log_parse_list = list()
        for log in self.log_list:
            lastBuff, bin_in_log, type_in_log = self.extract_info_from_log(log.get("content"))
            log_parse_list.append(self.bin_api.get_cmd_decode(lastBuff))
        return log_parse_list

    def extract_info_from_log(self, data):
        lastBuff, bin_in_log, type_in_log = "", -1, -1
        pattern_bin = r'\[device\]\[\d+\]\[bin.(\d+)\]'
        match = re.search(pattern_bin, data)
        if match:
            bin_in_log = match.group(1)
        pattern_lastbuff = r'"lastBuff":"([^"]+)"'
        match = re.search(pattern_lastbuff, data)
        if match:
            lastBuff = match.group(1)
        pattern_type = r'\\"type\\":(\d+)'
        match = re.search(pattern_type, data)
        if match:
            type_in_log = match.group(1)
        return lastBuff, int(bin_in_log), int(type_in_log)


class AliyunOss(object):

    def __init__(self, access_keyID=None, access_key=None, endpoint=None, bucket_name='xc-res', file_type='firmware'):
        self.file_type       = file_type
        self.access_keyID    = access_keyID or config.ALIYUN_OSS_ACCESSKEYID
        self.access_key      = access_key or config.ALIYUN_OSS_ACCESSKEY
        self.endpoint        = endpoint or config.ALIYUN_OSS_ENDPOINT
        self.bucket_name     = bucket_name
        self.auth            = oss2.Auth(access_key_id=self.access_keyID, access_key_secret=self.access_key)
        self.bucket          = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        self.oss_file_path   = f'xatool/{self.file_type}/'
        self.local_file_path = os.path.join(os.path.dirname(__file__), "..", "resources")

    def put(self, file_name='test.123', local_file_name='test.123'):
        """上传文件到阿里云OSS，文件统一从resources上传
        Args:
            file_name (str, optional): 上传到aliyun的文件名. Defaults to 'test.123'.
            local_file_name (str, optional): 本地文件名. Defaults to 'test.123'.
        """        
        if not os.path.isabs(local_file_name):
            local_file_name = os.path.join(self.local_file_path, local_file_name)
        self.bucket.put_object_from_file(
            self.oss_file_path + os.path.basename(file_name), local_file_name)
        logger.info(f"File {local_file_name} uploaded successfully.")
        # TODO(修改路径获取方式)
        return 'http://xc-res.oss-cn-shenzhen.aliyuncs.com/xatool/firmware/{}'.format(config.upgrade_pack)

    def download(self, remote_file_name):
        try:
            self.bucket.get_object_to_file(
                key=self.oss_file_path + remote_file_name, filename=os.path.join(self.local_file_path, remote_file_name))
            logger.info(f"download {remote_file_name} successfully.")
        except:
            return False
        return True


if __name__ == "__main__":
    aliyun_log = AliyunLog()
    log_list = aliyun_log.query_logs(
        15, query_string="860957074281841", bin=5, log_type=8)
    print(log_list)
    # oss_instance = AliyunOss()
    # # oss_instance.put()
    # oss_instance.download("test.123")
    pass