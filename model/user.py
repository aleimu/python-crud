# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from base import Base, db
from sqlalchemy import Integer, Column, String, TEXT, TIMESTAMP
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), index=True, unique=True)  # 登录名
    password = Column('hash', String(256), nullable=False)
    fullname = Column(String(32))  # 姓名
    email = Column(String(64))
    telephone = Column(String(12))  # 座机号
    # status = Column(Integer, default=0)  # 激活状态(0：未激活；1：已激活)
    role_type = Column(Integer)  # 角色类型
    reason = Column(String(100))  # 注销/禁用账号的理由
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)
