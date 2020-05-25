# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'
__doc__ = "通用函数,适配flask特性的一些常用函数,降低重复操作,精简代码量"

import time
from flask import json, request
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
