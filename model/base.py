# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from app import db


class Base(db.Model):
    # __tablename__ = 'tablename'
    __bind_key__ = 'db1'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.TIMESTAMP, default=datetime.now)
    update_time = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        dict = {}
        dict.update(self.__dict__)
        if "_sa_instance_state" in dict:
            del dict['_sa_instance_state']
        return dict

    @staticmethod
    def first(id):
        base_obj = Base.query.filter_by(id=id).first_or_404()
        return base_obj
