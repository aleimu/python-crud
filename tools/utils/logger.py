# -*- coding:utf-8 -*-
__author__ = "q.p"
__doc__ = "带有上下文的log实现"

import os
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_NAME = "python_curl.log"
LOG_LEVEL = "INFO"

log_path = os.path.realpath(os.getcwd()) + '/logs/'  # 文件路径

init_logger = logging.getLogger(LOG_NAME)
init_logger.setLevel(LOG_LEVEL)
# 日志格式
log_format = '%(asctime)s|%(process)d|%(levelname)s|%(filename)s|%(funcName)s|%(lineno)d|%(keyword)s|%(user)s|%(action)s|%(obj)s|%(obj_id)s|%(result)s|%(type)s|%(message)s'
file_format = logging.Formatter(log_format)
# 日志轮转
# tr_handler = TimedRotatingFileHandler(log_path + LOG_NAME, when='midnight', encoding='utf-8')
# tr_handler.setFormatter(file_format)
# tr_handler.suffix = "_%Y%m%d.log"
# init_logger.addHandler(tr_handler)
# 控制台日志 --本地调试时打开
import sys

h_console = logging.StreamHandler(sys.stdout)
h_console.setFormatter(file_format)
h_console.setLevel(logging.DEBUG)
init_logger.addHandler(h_console)

# 设定默认值
extra_dict = {"user": "", "type": "", "keyword": "", "action": "", "obj": "", "obj_id": "", "result": ""}


class LoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs["extra"] = self.extra
        else:
            for k in self.extra.keys():
                if k not in kwargs['extra'].keys():
                    kwargs['extra'][k] = self.extra[k]
        return msg, kwargs


# LoggerAdapter构造方法的logger实例
logger = LoggerAdapter(init_logger, extra=extra_dict)

if __name__ == '__main__':
    # 应用中的日志记录方法调用
    import time

    t1 = time.time()
    for x in range(10):
        logger.info("User Login!")
        logger.info("User Login!", extra={"action": "113.208.78.29", "user": "Petter1"})
        logger.info("User Login!", extra={"user": "Petter2"})
        logger.debug("User Login!")
    t2 = time.time()
    print(t2 - t1)
