# -*- coding:utf-8 -*-
__doc__ = "数据库单例模式"


class InitDB(object):
    def __init__(self):
        self.handle = None
        self.helper = None

    def set(self, handle, **kwargs):
        self.handle = handle
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, item):
        return getattr(self.handle, item)

    def get(self):
        return self.handle


db = InitDB()
