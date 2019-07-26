# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'
__doc__ = "装饰器"

from flask import g
from tools import json_response, js
from flask import json, jsonify, make_response, request, abort
from functools import wraps
from constant import PARAM_ERR



def validate_params(required=None):
    """简单的必须参数检查 --- 更复杂的校验使用common.JsonParser"""

    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            params_dict = request.values.to_dict()
            if request.json:
                params_dict.update(request.json)
            for arg in required:
                if not params_dict.get(arg, None):
                    return js(PARAM_ERR, '%s 参数缺失' % arg, {})
            val = func(*args, **kwargs)
            return val

        return decorated_func

    return decorator


def check_permission(str_code):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not g.user.is_supper:
                or_list = [x.strip() for x in str_code.split('|')]
                for or_item in or_list:
                    and_set = {x.strip() for x in or_item.split('&')}
                    if and_set.issubset(g.user.permissions):
                        break
                else:
                    return json_response(403, message='Permission denied')
            return func(*args, **kwargs)

        return wrapper

    return decorate


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer, Accept, Origin, User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst

    return wrapper_fun
