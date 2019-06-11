import logging
import time
import traceback

from django.conf import settings
from aliyun.log import LogClient, LogItem, PutLogsRequest

LOCAL_LOG = 1
SERVER_LOG = 2
BOTH_LOG = 3


class Log(object):
    def __init__(self, location):
        self.logger = logging.getLogger(location)
        self.location = location

    def info(self, message):
        self.__log_proxy('info', message)

    def debug(self, message):
        self.__log_proxy('debug', message)

    def error(self, message):
        self.__log_proxy('error', message)

    def warning(self, message):
        self.__log_proxy('warning', message)

    def __log_proxy(self, function, message):
        # 获取日志记录的点相关信息
        trace = traceback.extract_stack()[-3]
        filename = str(trace.filename)

        file_list = filename.split('/')
        filename_file = file_list[-2]
        filename_function = file_list[-1]
        filename_function = filename_function[:filename_function.rfind('.')]
        filename = f'{filename_file}.{filename_function}'

        function_name = trace.name
        lineno = trace.lineno
        log_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        message = f'time:{log_time} file:{filename} function:{function_name} lineno:{lineno} log_type:{function} ' \
                  f'【message:{message}】'

        if settings.LOG_TYPE == LOCAL_LOG:
            log_function = getattr(self.logger, function)
            log_function(message)

        elif settings.LOG_TYPE == SERVER_LOG:
            send_log_to_aliyun(self.location, message)
        else:
            log_function = getattr(self.logger, function)
            log_function(message)
            send_log_to_aliyun(self.location, message)


def send_log_to_aliyun(logstore, message):
    """
    向阿里云日志系统 发送log函数
    :param message:  将要发送的log字符串
    :return:  None
    """
    # 构建一个 client 使用 client 实例的方法来操作日志服务
    client = LogClient(settings.END_POINT, settings.ACCESS_KEY_ID, settings.ACCESS_KEY)
    log_item = LogItem()
    log_item.set_time(int(time.time()))
    log_item.set_contents([('message', message)])
    put_logs_request = PutLogsRequest(settings.PROJECT, logstore, '', '', [log_item])
    client.put_logs(put_logs_request)  # 发送log
