# -*- coding:utf-8 -*-
__doc__ = "数据库单例.模块"


class InstanceDB(object):
    def __init__(self):
        self.handle = None
        self.helper = None

    def __getattr__(self, item):
        """适配SQLAlchemy的属性获取"""
        return getattr(self.handle, item)

    def set(self, handle, **kwargs):
        """
        绑定db实例,用于数据库session切换
        :param handle:db实例
        :param kwargs: read_db=read_db_name,write_db=write_db_name
        :return:None
        """
        self.handle = handle
        for k, v in kwargs.items():  # 将依赖的db_name设置到Instance实例
            setattr(self, k, v)

    def get(self, db_name):
        """
        系统获取db_name
        :param db_name: 特定系统关联的数据库名称
        :return:
        """
        try:
            db_name = getattr(self, db_name)
        except AttributeError as e:
            print("Do not set the database name, check it out:%s" % e.message)
        return db_name


db = InstanceDB()
