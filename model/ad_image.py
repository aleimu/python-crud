# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from .base import Base, db


class ad_image(Base):  # 资源分组中的图片
    __tablename__ = 'ad_image'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.String(64), nullable=False)  # 组名ad_group.id
    image_name = db.Column(db.String(100))  # 图片存放链接
    image_url = db.Column(db.String(100))  # 图片存放链接
    note = db.Column(db.String(10))  # 备注
    create_time = db.Column(db.TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
