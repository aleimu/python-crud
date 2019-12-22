# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"
__doc__ = "资源分组"

from base import *


class AdGroup(Base):
    __tablename__ = 'ad_group'
    __bind_key__ = db.read_db

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(10), nullable=False)  # 组名  1:系统A, 2:系统B, 3:系统C ...
    note = db.Column(String(20))  # 备注
    create_time = db.Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = db.Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间


class AdGroup2(Base):
    __tablename__ = 'ad_group'
    __bind_key__ = db.write_db
    __table_args__ = {
        'schema': db.write_db,
        "extend_existing": True
    }

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(10), nullable=False)  # 组名  1:系统A, 2:系统B, 3:系统C ...
    note = db.Column(String(20))  # 备注
    create_time = db.Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = db.Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
