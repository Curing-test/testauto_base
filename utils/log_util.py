
import logging
import time
from logging import handlers
import os
from utils.file_util import mkdir


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename='', level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s'):
        self.log_dir = os.path.join(os.path.dirname(__file__), "..", "log")
        # print(self.log_dir)
        if not filename:
            filename = self.get_log_path()
        if not os.path.isabs(filename):
            filename = os.path.join(self.log_dir, filename)
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)  # 设置文件里写入的格式
        if not self.logger.handlers:
            self.logger.addHandler(sh)  # 把对象加到logger里
            self.logger.addHandler(th)

    def get_log_path(self, log_file_prefix='xatest-'):
        nowtime = time.localtime()
        # strftime = time.strftime("%Y%m%d_%H-%M-%S", nowtime)
        strftime = time.strftime("%Y%m%d", nowtime)
        logfile = os.path.join(
            self.log_dir, f"{log_file_prefix}-{strftime}.log")
        if not os.path.exists(self.log_dir):
            mkdir(self.log_dir)
        return logfile


if __name__ == '__main__':
    log = Logger(level='debug')
    log.logger.debug('debug')
    log.logger.info('info')
    log = Logger(level='error')
    log.logger.warning('警告')
    log.logger.error('报错')
    log.logger.critical('严重')
    Logger('error.log', level='error').logger.error('error')
