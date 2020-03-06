# -*- coding:utf-8 -*-
__doc__ = "数据库单例.模块"


class InstanceDB(object):
    def __init__(self):
        self.handle = None
        self.helper = None
        self.already_set = set()  # 抑制同一错误重复打印

    def __getattr__(self, item):
        """适配SQLAlchemy的属性获取,参考readme.md使用"""
        if not self.handle:
            raise Exception("model与db实例未真正绑定, 请保证使用model前已执行db.set, 参考readme.md使用!")
        return getattr(self.handle, item)

    def set(self, handle, **kwargs):
        """
        绑定db实例
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
            if db_name not in self.already_set:
                self.already_set.add(db_name)
                print("未设置数据库名,请检查此:%s model代码!" % e.message)
        return db_name


db = InstanceDB()
