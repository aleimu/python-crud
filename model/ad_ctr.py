# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from .base import Base, db


class ad_ctr(Base):  # 一个系统中的一个广告的日点击情况
    __tablename__ = 'ad_ctr'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(64), nullable=False)  # 广告编号-> redis key
    show_count = db.Column(db.Integer, default=0)  # 全天总曝光量
    click_count = db.Column(db.Integer, default=0)  # 全天总点击量
    crt = db.Column(db.String(10))  # 全天点击率
    show_day = db.Column(db.String(100))  # 全天时段曝光量 json_str
    click_day = db.Column(db.String(100))  # 全天时段点击量 json_str
    note = db.Column(db.String(10))  # 备注
    create_date = db.Column(db.TIMESTAMP, default=datetime.now)  # 天数
    create_time = db.Column(db.TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
