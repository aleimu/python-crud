# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from .base import Base, db
from sqlalchemy import Integer, Column, String, TEXT, TIMESTAMP


class ad_style(db.Model, Base):  # 广告展示方式与设置
    __tablename__ = 'ad_style'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False)  # 广告编号-> redis key
    group_id = Column(Integer, index=True, default=0)  # 分组id :ad_group.id
    image_id = Column(Integer, default=0)  # 图片id ->ad_image.id
    oper_uid = Column(Integer)  # 操作人id;user.id
    oper_uname = Column(String(11))  # 操作人username
    status = Column(Integer, default=2)  # 状态(0：已下架 1：已上架 2:暂存未发布 3:已删除弃用)  -> 同一个位置只能上架一个产品和图片展示方式有关
    close = Column(Integer, default=0)  # 是否可点击关闭(0：可关闭；1：不可关闭 )
    mode = Column(Integer, default=0)  # 图片展示方式: 轮播,横幅
    frequency = Column(String(5), default=0.5)  # 图片轮播的频率0.1-0.5s
    position = Column(String(5), default=1)  # 图片摆放位置: 1:首页banner,2:首页底部,3:商场banner
    system = Column(Integer, default=1)  # 1: driver_advert, 2:dispatch_advert, 3:order_advert, 4: camel_advert
    note = Column(String(32))  # 备注
    up_time = Column(TIMESTAMP, default=datetime.now)  # 上架时间
    down_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 下架时间
    create_time = Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
