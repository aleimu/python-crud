# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

import uuid
import redis
from redis.exceptions import ConnectionError
from app.config import *

rds = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB, socket_timeout=3000)
rds_token = 'token:{}'.format


def rds_hmset(key, value, expire=3600):
    rds.hmset(key, value)
    rds.expire(key, expire)


def make_token(username):
    token = str(uuid.uuid1())
    token = token[0:len(token) - len(username)] + username
    return token


def delect_token(username):
    match = "token:*%s" % username
    result = rds.scan_iter(match=match, count=10000)
    for key in result:
        if rds.hget(key, 'username') == username:
            rds.delete(key)


def verify_token(token):
    pass


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
