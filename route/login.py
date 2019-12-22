# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

from flask import Blueprint, request

from tools.model import User
from tools.utils import OK, LOGIN_FAIL, PARAM_ERR, validate_params, js, first2dict
from cache import rds, make_token, rds_hmset, rds_token
from app import db

auth = Blueprint('auth', __name__, url_prefix='/v1/user')


@auth.route('/login', methods=['POST', 'GET'])
@validate_params(['username', 'password'])
def login():
    username = request.values.get('username')
    password = request.values.get('password')
    user_obj = User.query.filter(User.username == username).first()
    print (first2dict(user_obj))
    if user_obj and user_obj.verify_password(password):
        token = make_token(user_obj.username)
        rds_hmset(rds_token(token), first2dict(user_obj))
        return js(OK, None, {"token": token, "username": username})
    else:
        return js(LOGIN_FAIL)


@auth.route('/logout')
def logout():
    token = request.args.get('token')
    if token:
        user_info = rds.hgetall(rds_token(token))
        if user_info:
            rds.delete(rds_token(token))
    return js(OK, None, "logout success")


@auth.route('/register', methods=['POST', 'GET'])
def register():
    username = request.values.get('username')
    password = request.values.get('password')
    if not all([username, password]):
        return js(PARAM_ERR, "参数缺失!")
    user_obj = User.query.filter(User.username == username).first()
    if user_obj:
        return js(PARAM_ERR, "用户名已存在!")
    user_obj = User(username=username, password=None, email=None, telephone=None, role_type=None,
                    fullname=username)
    user_obj.set_password(password)
    print(user_obj)
    db.session.add(user_obj)
    db.session.commit()
    return js(OK, "注册成功!")
