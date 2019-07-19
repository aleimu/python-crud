# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from .base import Base, db


class User(Base):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True, unique=True)  # 登录名
    password = db.Column(db.String(256), nullable=False)
    fullname = db.Column(db.String(32))  # 姓名
    user_no = db.Column(db.String(32), index=True, unique=True)  # 用户工号
    email = db.Column(db.String(64))
    telephone = db.Column(db.String(12))  # 座机号
    status = db.Column(db.Integer, default=0)  # 激活状态(0：未激活；1：已激活)
    role_type = db.Column(db.Integer)  # 角色类型
    user_type = db.Column(db.Integer, default=2)  # 用户类型
    photo_url = db.Column(db.TEXT)
    source = db.Column(db.Integer, default=1)  # 来源
    reason = db.Column(db.String(100))  # 注销/禁用账号的理由
    create_time = db.Column(db.TIMESTAMP, default=datetime.now)
    update_time = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
