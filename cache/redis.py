# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

import traceback
import redis
from redis.exceptions import ConnectionError
from app.logger import logger
from app.config import *
from cache.keys import key_token

rds = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB, socket_timeout=3000)


# 初始化或搜索缓存中的用户信息
def deco_user_cache(func):
    def wrapper(*args, **kwargs):
        try:
            value = rds.hgetall(kwargs['key'])
            logger.debug('try search in cache, key: %s ,found value: %s' % (kwargs['key'], value))
            if value:
                for key in value:
                    value[key] = value[key].decode(encoding='UTF-8', errors='strict')
                return None, value
            err, user_dict = func(*args, **kwargs)
            if user_dict:  # 初始化登录信息
                key = kwargs['key']
                rds.hmset(key, user_dict)
                rds.expire(key, LOGIN_EXPIRE)
            return err, user_dict
        except:
            logger.error(traceback.format_exc())
            raise

    return wrapper


def get_session(token):
    key = key_token(token)
    return None, rds.hgetall(key)


def delect_user_token(username):
    match = "token:*%s" % username
    result = rds.scan_iter(match=match, count=10000)
    for key in result:
        if rds.hget(key, 'username') == username:
            rds.delete(key)


def deco_update(func):
    def wrapper(*args, **kwargs):
        val = func(*args, **kwargs)
        n_val = val[1]
        if not n_val:
            return val
        o_val = rds.hgetall(kwargs['key'])
        if o_val:
            for k in o_val:
                if k in n_val and n_val[k] and o_val[k] != n_val[k]:
                    o_val[k] = n_val[k]
            rds.hmset(kwargs['key'], o_val)
        return None, n_val

    return wrapper
