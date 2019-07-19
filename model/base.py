# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from app import db
from sqlalchemy import Integer, Column, String, TEXT, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base


class CommonBase(object):
    # __tablename__ = 'tablename'
    # __bind_key__ = 'db1'

    # id = Column(Integer, primary_key=True, autoincrement=True)
    # create_time = Column(TIMESTAMP, default=datetime.now)
    # update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        dict = {}
        dict.update(self.__dict__)
        if "_sa_instance_state" in dict:
            del dict['_sa_instance_state']
        return dict

    @classmethod
    def to_first(self, **kwargs):
        obj = self.query.filter_by(**kwargs).first()
        return obj

    @classmethod
    def to_all(self, **kwargs):
        obj = self.query.filter_by(**kwargs).all()
        return obj

    #
    # @classmethod
    # def check_exists(self, **kwargs):
    #     bl = db.session.query(self.query.filter_by(**kwargs).exists()).scalar() is not None
    #     return bl


Base = declarative_base(cls=CommonBase)
