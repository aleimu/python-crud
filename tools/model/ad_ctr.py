# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"
__doc__ = "一个系统中的一个广告的日点击情况"

from base import *


class AdCtr(Base):
    __tablename__ = 'ad_ctr'
    __bind_key__ = db.read_db  # 读写库区分

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False)  # 广告编号-> redis key
    show_count = Column(Integer, default=0)  # 全天总曝光量
    click_count = Column(Integer, default=0)  # 全天总点击量
    crt = Column(Float(3))  # 全天点击率
    show_day = Column(String(300))  # 全天时段曝光量 json_str
    click_day = Column(String(300))  # 全天时段点击量 json_str
    note = Column(String(10))  # 备注
    create_date = Column(TIMESTAMP, default=datetime.now)  # 天数
    create_time = Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间


class AdCtr2(Base):
    __tablename__ = 'ad_ctr'
    __bind_key__ = db.write_db  # 读写库区分
    __table_args__ = {
        'schema': db.write_db,  # 读写库区分
        "extend_existing": True  # 允许表名重复
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False)  # 广告编号-> redis key
    show_count = Column(Integer, default=0)  # 全天总曝光量
    click_count = Column(Integer, default=0)  # 全天总点击量
    crt = Column(Float(3))  # 全天点击率
    show_day = Column(String(300))  # 全天时段曝光量 json_str
    click_day = Column(String(300))  # 全天时段点击量 json_str
    note = Column(String(10))  # 备注
    create_date = Column(TIMESTAMP, default=datetime.now)  # 天数
    create_time = Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
