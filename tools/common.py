# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'
__doc__ = "通用函数,适配flask特性的一些常用函数,降低重复操作,精简代码量"

import time
import datetime
from flask import json, jsonify, make_response, request, abort
from functools import wraps
from constant import PARAM_ERR, ALLOWED_EXTENSIONS
from sqlalchemy.ext.declarative import DeclarativeMeta


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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


def js(code, err=None, data=None):
    """
    与前端通用的交互格式
    :param code:
    :param errmsg:
    :param data:
    :return:
    """
    return jsonify({'code': code, 'errmsg': err, 'data': data})


def validate_params(required=None):
    """必须参数检查"""

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


class APIEncoder(json.JSONEncoder):
    """
    改变复杂数据结构的json编译策略
    """

    def default(self, obj):
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
            # 应该先转换成dict如 return jsonify({'code': 1800, 'data': first2dict(sql_obj2), 'errmsg': None})
            # 或者 return jsonify({'code': 1800, 'data': all2dict(sql_obj2), 'errmsg': None})
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


def values2db(values, db_model, inspect=(), space=False, alias=None):
    """
    将request.values装换为db实例: 1.限定值范围 2.别名 3.修改""为None
    :param values: request.values,{keys:values}
    :param db_model: 实例化的db模型
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
            if space and not var:
                var = None
            if hasattr(db_model, arg) and arg in inspect:
                setattr(db_model, arg, var)
            else:
                abort(405, "not find:%s" % arg)

    return db_model


def get_arg(type='values'):
    if hasattr(request, type):
        return getattr(request, type)
    else:
        abort(500)


def time_cmp(first_time, second_time, fomat="('%Y-%m-%d %H:%M:%S')"):
    """字符串形式的时间比较大小"""
    return int(time.strftime(fomat, first_time)) - int(time.strftime(fomat, second_time))
