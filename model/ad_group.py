# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from .base import Base, db
from sqlalchemy import Integer, Column, String, TEXT, TIMESTAMP


class ad_group(db.Model, Base):  # 资源分组
    __tablename__ = 'ad_group'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    group = db.Column(String(10), nullable=False)  # 组名  1:司机端, 2:订单系统, 3:承运商系统等
    note = db.Column(String(20))  # 备注
    create_time = db.Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = db.Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间