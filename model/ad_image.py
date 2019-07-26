# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from base import Base, db
from sqlalchemy import Integer, Column, String, TEXT, TIMESTAMP


class ad_image(db.Model, Base):  # 资源分组中的图片
    __tablename__ = 'ad_image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, nullable=False)  # 组名ad_group.id
    image_name = Column(String(100))  # 图片存放链接
    image_url = Column(String(100))  # 图片存放链接
    note = Column(String(10))  # 备注
    create_time = Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
