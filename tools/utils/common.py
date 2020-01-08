# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'
__doc__ = "通用函数,适配flask特性的一些常用函数,降低重复操作,精简代码量"

import time
import datetime
from flask import json, jsonify, request, abort
from .constant import PARAM_ERR, ALLOWED_EXTENSIONS
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


def time_cmp(first_time, second_time, fomat="('%Y-%m-%d %H:%M:%S')"):
    """字符串形式的时间比较大小"""
    return int(time.strftime(fomat, first_time)) - int(time.strftime(fomat, second_time))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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
            # sql_obj = User.query.filter(User.com_name == com_name).first()
            # return jsonify({'code': 1800, 'data': sql_obj, 'errmsg': None})

            # 不可以解析 sql_obj2 = db.session.query(User.com_name, User.legalp_name, User.contact_name).
            # filter(User.com_name == com_name).first()
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
    db_obj = User.query.filter(XXXXX).order_by(User.create_time.desc()).paginate(page, per_page, False).items
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
    db_obj = User.query.filter(XXXXX).first()
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
            if space and not var:
                var = None
            if hasattr(db_model, arg) and arg in inspect:
                setattr(db_model, arg, var)
            else:
                abort(405, "not find:%s" % arg)

    return db_model


class ParseError(BaseException):
    def __init__(self, message):
        self.message = message


class AttrDict(dict):
    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __delattr__(self, item):
        self.__delitem__(item)


class Argument(object):
    """
    :param name: name of option
    :param default: default value if the argument if absent
    :param bool required: is required
    """

    def __init__(self, name, default=None, required=True, type=None, filter=None, help=None, nullable=False):
        self.name = name
        self.default = default
        self.type = type
        self.required = required
        self.nullable = nullable
        self.filter = filter
        self.help = help
        if not isinstance(self.name, str):
            raise TypeError('Argument name must be string')
        if filter and not callable(self.filter):
            raise TypeError('Argument filter is not callable')

    def parse(self, has_key, value):
        if not has_key:
            if self.required and self.default is None:
                raise ParseError(self.help or 'Required Error: %s is required' % self.name)
            else:
                return self.default
        elif value in [u'', '', None]:
            if self.default is not None:
                return self.default
            elif not self.nullable and self.required:
                raise ParseError(self.help or 'Value Error: %s must not be null' % self.name)
            else:
                return None
        try:
            if self.type:
                if self.type in (list, dict) and isinstance(value, str):
                    value = json.loads(value)
                    assert isinstance(value, self.type)
                elif self.type == bool and isinstance(value, str):
                    assert value.lower() in ['true', 'false']
                    value = value.lower() == 'true'
                elif not isinstance(value, self.type):
                    value = self.type(value)
        except (TypeError, ValueError, AssertionError):
            raise ParseError(self.help or 'Type Error: %s type must be %s' % (self.name, self.type))

        if self.filter:
            if not self.filter(value):
                raise ParseError(self.help or 'Value Error: %s filter check failed' % self.name)
        return value


class BaseParser(object):
    def __init__(self, *args):
        self.args = []
        for e in args:
            if isinstance(e, str):
                e = Argument(e)
            elif not isinstance(e, Argument):
                raise TypeError('%r is not instance of Argument' % e)
            self.args.append(e)

    def _get(self, key):
        raise NotImplementedError

    def _init(self, data):
        raise NotImplementedError

    def add_argument(self, **kwargs):
        self.args.append(Argument(**kwargs))

    def parse(self, data=None):
        rst = AttrDict()
        try:
            self._init(data)
            for e in self.args:
                rst[e.name] = e.parse(*self._get(e.name))
        except ParseError as err:
            return None, err.message
        return rst, None


class JsonParser(BaseParser):
    def __init__(self, *args):
        self.__data = None
        super(JsonParser, self).__init__(*args)

    def _get(self, key):
        return key in self.__data, self.__data.get(key)

    def _init(self, data, source=request):
        if data is None:
            try:
                self.__data = source.args.to_dict()
                post_json = source.get_json()
            except Exception as e:
                raise ParseError('Invalid data source for parse')
            if isinstance(post_json, dict):
                self.__data.update(post_json or {})
        else:
            try:
                if isinstance(data, (str, bytes)):
                    data = data.decode('utf-8')
                    self.__data = json.loads(data) if data else {}
                else:
                    assert hasattr(data, '__contains__')
                    assert hasattr(data, 'get')
                    assert callable(data.get)
                    self.__data = data
            except (ValueError, AssertionError):
                raise ParseError('Invalid data type for parse')


""" 使用样例
form, error = JsonParser(
    Argument('app_id', type=int),
    Argument('env_id', type=int),
    Argument('deploy_message', default=''),
    Argument('deploy_restart', type=bool),
    Argument('host_ids', type=list)
).parse()
"""
