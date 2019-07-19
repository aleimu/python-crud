# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

from flask import Blueprint, request
from tools import constant as cs, validate_params, js
from cache import rds, key_token

auth = Blueprint('auth', __name__, url_prefix='/v1/auth')


@auth.route('/login', methods=['POST', 'GET'])
@validate_params(['username', 'password'])
def web_login():
    username = request.values.get('username')
    password = request.values.get('password')
    pass  # 自己写吧


@auth.route('/logout')
def web_logout():
    token = request.args.get('token')
    if token:
        user_info = rds.hgetall(key_token(token))
        if not user_info:
            return js(cs.SERVER_ERR, None, "logout failed")
    return js(cs.OK, None, "logout success")
