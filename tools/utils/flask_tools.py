#!/usr/bin/python
# -*- coding:utf-8 -*-
__doc__ = "适配flask"

import datetime
from flask import json, Response, make_response, jsonify, request, abort
from functools import wraps
from decimal import Decimal
from sqlalchemy.ext.declarative import DeclarativeMeta


def get_page():
    """分页操作"""
    data = request.values.to_dict()
    if request.method == "GET":
        page_index = int(data.get('page_index', 1) if data.get('page_index', 1) else 1)
        page_size = int(data.get('page_size', 10) if data.get('page_size', 10) else 10)
    else:
        page_index = None
        page_size = None
    return page_index, page_size


def request_data():
    """
    获取request中的全部参数包括params和json中
    :return:
    """
    req_dict = request.values.to_dict()  # 只能获取params中的
    if request.method in ('POST', 'PUT'):
        if request.json and isinstance(request.json, dict):
            req_dict.update(request.json)
    return req_dict


class APIEncoder(json.JSONEncoder):
    """
    改变复杂数据结构的json编译策略
    """

    def default(self, obj):
        if isinstance(obj, Decimal):  # FIXME
            return float(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj.__class__, DeclarativeMeta):  # 配合 isinstance(obj, dict)
            return self.default({i.name: getattr(obj, i.name) for i in obj.__table__.columns})
        elif isinstance(obj, dict):
            # 只可以解析这样的sql查询,如下:
            # sql_obj = Shipper.query.filter(Shipper.com_name == com_name).first()
            # return jsonify({'code': 1800, 'data': sql_obj, 'errmsg': None})

            # 不可以解析 sql_obj2 = db.session.query(Shipper.com_name, Shipper.legalp_name, Shipper.contact_name).
            # filter(Shipper.com_name == com_name).first()
            # return jsonify({'code': 1800, 'data': sql_obj2, 'errmsg': None})
            # 应该先转换成dict如 return jsonify({'code': 1800, 'data': first_to_dict(sql_obj2), 'errmsg': None})
            # 或者 return jsonify({'code': 1800, 'data': all_to_dict(sql_obj2), 'errmsg': None})
            new_dict = {}
            for k in obj:
                try:
                    if isinstance(obj[k], (datetime.datetime, datetime.date, DeclarativeMeta)):
                        new_dict[k] = self.default(obj[k])
                    else:
                        new_dict[k] = obj[k]
                except TypeError:
                    new_dict[k] = None
            return new_dict
        return json.JSONEncoder.default(self, obj)


def all2dict(db_obj):
    """
    db_obj = db.session.query.filter(XXXXX).all() 的查询结果转成dict样式,注意结果包含在 [] 内,注意与前端的解析
    db_obj = Shipper.query.filter(XXXXX).order_by(Shipper.create_time.desc()).paginate(page, per_page, False).items
    :param db_obj: db.session.query.filter(XXXXX).all() 的查询结果
    :return:list[dict,dict,...]
    """
    new_list = []
    if not db_obj:
        return new_list
    if isinstance(db_obj, list):
        for x in db_obj:
            new_list.append(first2dict(x))
        return new_list
    else:
        return first2dict(db_obj)


def first2dict(db_obj):
    """
    db_obj = db.session.filter(XXXXX).first() 的查询结果转成dict样式
    db_obj = Shipper.query.filter(XXXXX).first()
    :param db_obj: db.session.filter(XXXXX).first() 的查询结果
    :return:dict
    """
    new_dict = dict()
    # print("db_obj:",type(db_obj),db_obj.keys())   # 'Truck' object has no attribute 'keys'
    if hasattr(db_obj, "keys") and callable(db_obj.keys):  # callable(getattr(db_obj ,'keys'))
        for k in db_obj.keys():
            try:
                if hasattr(db_obj, k):
                    new_dict[k] = getattr(db_obj, k)
                else:
                    new_dict[k] = None
            except TypeError:
                new_dict[k] = None
    else:
        new_dict = vars(db_obj)
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
    return new_dict


def values2model(values, db_model, inspect=(), space=False, alias=None):
    """
    将request.values装换为db实例: 1.限定值范围 2.别名 3.修改""为None
    :param values: request.values,{keys:values}
    :param db_model: 实例化的db模型如 User()
    :param alias: 别名,请求入参名称和数据库对应不上时使用
    :param inspect: 转换别名后,数据库需要的字段
    :param space: values中的空值转化成None写入数据库NULL
    :return:
    """
    if hasattr(values, "keys") and callable(values.keys):
        for arg in values.keys():
            if alias and arg in alias:
                var = values.get(arg)
                arg = alias.get(arg)
            else:
                var = values.get(arg)
            if arg not in inspect:
                continue
            if space and not var:
                var = None
            if hasattr(db_model, arg):
                setattr(db_model, arg, var)
            else:
                raise Exception("not find:%s" % arg)
    return db_model


def get_arg(source='values'):
    if hasattr(request, source):
        return getattr(request, source)
    else:
        abort(500)


def js(code, err=None, data=None):
    """
    与前端通用的交互格式
    :param code:
    :param errmsg:
    :param data:
    :return:
    """
    return jsonify({'code': code, 'errmsg': err, 'data': data})


def json_response(code, data=None, message=None):
    if isinstance(data, list) and all([hasattr(x, 'to_json') for x in data]):
        data = [x.to_json() for x in data]
    elif isinstance(data, DeclarativeMeta) and hasattr(data, 'to_json'):
        data = data.to_json()
    return js(code, message, data)


def rw(code, data=None):
    """
    与前端通用的交互格式
    """
    if isinstance(data, dict) and data.get('msg'):
        return jsonify({'code': code[0], 'errmsg': data.get('msg'), 'data': data})
    return jsonify({'code': code[0], 'errmsg': code[1], 'data': data})


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        allow_headers = "Referer, Accept, Origin, User-Agent, x-requested-with"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst

    return wrapper_fun


def validate_params(required=None):
    """必须参数检查"""

    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            params_dict = request_data()
            if required:
                for arg in required:
                    if not params_dict.get(arg, None):
                        return rw((1001, '%s 参数缺失' % arg), {})
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
