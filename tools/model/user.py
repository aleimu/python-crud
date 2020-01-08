# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from .base import *
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'user'
    __bind_key__ = db.get("read_db")

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), index=True, unique=True)  # 登录名
    password = Column('pwd', String(256), nullable=False)
    fullname = Column(String(32))  # 姓名
    email = Column(String(64))
    telephone = Column(EncryptedType)  # 座机号
    status = Column(Integer, default=0)  # 激活状态(0：未激活；1：已激活)
    role_type = Column(Integer)  # 角色类型
    reason = Column(String(100))  # 注销/禁用账号的理由
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class User2(Base):
    __tablename__ = 'user'
    __bind_key__ = db.get("write_db")
    __table_args__ = {
        'schema': db.get("write_db"),
        "extend_existing": True
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), index=True, unique=True)  # 登录名
    password = Column('pwd', String(256), nullable=False)
    fullname = Column(String(32))  # 姓名
    email = Column(String(64))
    telephone = Column(EncryptedType)  # 座机号
    status = Column(Integer, default=0)  # 激活状态(0：未激活；1：已激活)
    role_type = Column(Integer)  # 角色类型
    reason = Column(String(100))  # 注销/禁用账号的理由
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)
