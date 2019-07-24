# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

SECRET_KEY = "123"
UPLOAD_FOLDER = "D:\project_tmp"
DATA_FOLDER = './app/static/assets/data/'
SMS_FLAG = True  # # 是否允许发短息
LOG_LEVEL = 'INFO'  # NOTSET,DEBUG,INFO,WARNING,ERR,CRITICAL
LOG_NAME = 'python_crud.log'
LOGIN_EXPIRE = 3600  # 登录过期时间

# redis缓存配置
REDIS_DB = 15
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PWD = ''

# 数据库配置
SQLALCHEMY_DATABASE_URI = 'mysql://name:pwd@127.0.0.1:3306/test?charset=utf8'
SQLALCHEMY_DATABASE_URI2 = 'mysql://name:pwd@127.0.0.1:3307/test?charset=utf8'
DATABASE_QUERY_TIMEOUT = 0.5
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_BINDS = {
    'db1': SQLALCHEMY_DATABASE_URI,
    'db2': SQLALCHEMY_DATABASE_URI2
}

# 异步任务推给Work的Celery配置:
REDIS_DB2 = 0
REDIS_HOST2 = '127.0.0.1'
REDIS_PORT2 = 6379
REDIS_PWD2 = 'XXX'
REDIS_URL_REQUEST = 'redis://:%s@%s:%s/%s' % (REDIS_PWD2, REDIS_HOST2, REDIS_PORT2, REDIS_DB2)
