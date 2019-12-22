# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from base import *
from .ad_group import AdGroup, AdGroup2


class AdImage(Base):  # 资源分组中的图片
    __tablename__ = 'ad_image'
    __bind_key__ = db.read_db

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('{}.ad_group.id'.format(db.read_db)), nullable=False)  # 组名ad_group.id
    image_name = Column(String(100))  # 图片存放链接
    image_url = Column(String(100))  # 图片存放链接
    note = Column(String(10))  # 备注
    create_time = Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
    #groups = db.relationship("AdGroup", uselist=False, foreign_keys=[group_id])


class AdImage2(Base):  # 资源分组中的图片
    __tablename__ = 'ad_image'
    __bind_key__ = db.write_db
    __table_args__ = {
        'schema': db.write_db,
        "extend_existing": True
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('{}.ad_group.id'.format(db.write_db)), nullable=False)  # 组名ad_group.id
    image_name = Column(String(100))  # 图片存放链接
    image_url = Column(String(100))  # 图片存放链接
    note = Column(String(10))  # 备注
    create_time = Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
    #groups = db.relationship("AdGroup2", uselist=False, foreign_keys=[group_id])
