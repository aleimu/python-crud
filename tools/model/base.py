# -*- coding:utf-8 -*-
__doc__ = "基础model+自定义加密类型EncryptedType"

import binascii
from Crypto.Cipher import AES
from datetime import datetime, date
from sqlalchemy import Column, ForeignKey, Index, String, TIMESTAMP, SmallInteger, Integer, TIMESTAMP, TEXT, Float, \
    Date, DateTime, TypeDecorator, DECIMAL
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import exists, and_
from sqlalchemy.exc import SQLAlchemyError
from tools.utils import db, OK, read_db, write_db

key = "The encryption key."


def db_session_commit():
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


class EncryptedType(TypeDecorator):  # 自定义的加解密后的字段类型
    impl = String

    def process_bind_param(self, value, dialect):
        return aes_encrypt(value)

    def process_result_value(self, value, dialect):
        return aes_decrypt(value)


def aes_encrypt(data):
    cipher = AES.new(key)
    data = data + (" " * (16 - (len(data) % 16)))
    return binascii.hexlify(cipher.encrypt(data))


def aes_decrypt(data):
    cipher = AES.new(key)
    return cipher.decrypt(binascii.unhexlify(data)).rstrip()


"""
Base = declarative_base()

class User(Base):
    __tablename__ = 'user_aes'

    id = Column(Integer, primary_key=True)
    value = Column("value", EncryptedType(40), nullable=False)
"""


class Base(db.Model):
    __abstract__ = True  # SQLAlchemy中的类继承必须设置 https://segmentfault.com/a/1190000018005342
    __slots__ = ()

    @classmethod
    def get_first(self, **kwargs):
        obj = self.query.filter_by(**kwargs).first()
        return obj

    @classmethod
    def get_all(self, **kwargs):
        obj = self.query.filter_by(**kwargs).all()
        return obj

    @classmethod
    def save(self):
        db.session.add(self)
        db_session_commit()
        return self

    @classmethod
    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db_session_commit()

    @classmethod
    def add(self):
        db.session.add(self)

    @classmethod
    def sub_query(cls, **kwargs):
        sub_q = cls.query.filter_by(**kwargs).subquery()
        return sub_q

    @classmethod
    def update(self, **kwargs):
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(self, k) and getattr(self, k) != v:
                required_commit = True
                setattr(self, k, v)
        if required_commit:
            db_session_commit()
        return required_commit

    @classmethod
    def upsert(self, where, **kwargs):
        """更新或新增"""
        record = self.query.filter_by(**where).first()
        if record:
            record.update(**kwargs)
        else:
            record = self(**kwargs).save()
        return record

    @classmethod
    def to_json(self, remove=None, choose=None):
        """
        json序列化
        :param remove: 排除的字段合集
        :param choose: 选中的字段合集
        :return: dict
        """
        if not hasattr(self, '__table__'):
            raise AssertionError('<%r> does not have attribute for __table__' % self)
        elif choose:
            return {i: getattr(self, i) for i in choose}
        elif remove:
            return {i.name: getattr(self, i.name) for i in self.__table__.columns if i.name not in remove}
        else:
            return {i.name: getattr(self, i.name) for i in self.__table__.columns}

    @classmethod
    def to_dict(self):
        dict = {}
        dict.update(self.__dict__)
        if "_sa_instance_state" in dict:
            del dict['_sa_instance_state']

        return dict
