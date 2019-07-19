# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from datetime import datetime
from .base import Base, db


class ad_style(Base):  # 广告展示方式与设置
    __tablename__ = 'ad_style'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(64), nullable=False)  # 广告编号-> redis key
    group_id = db.Column(db.String(32), index=True, default=0)  # 分组id :ad_group.id
    image_id = db.Column(db.String(100), default=0)  # 图片id ->ad_image.id
    oper_uid = db.Column(db.String(11))  # 操作人id;user.id
    oper_uname = db.Column(db.String(11))  # 操作人username
    status = db.Column(db.Integer, default=2)  # 状态(0：已下架 1：已上架 2:暂存未发布 3:已删除弃用)  -> 同一个位置只能上架一个产品和图片展示方式有关
    close = db.Column(db.Integer, default=0)  # 是否可点击关闭(0：可关闭；1：不可关闭 )
    mode = db.Column(db.String(11), default=0)  # 图片展示方式: 轮播,横幅
    frequency = db.Column(db.String(11), default=0.5)  # 图片轮播的频率0.1-0.5s
    position = db.Column(db.String(11), default=1)  # 图片摆放位置: 1:首页banner,2:首页底部,3:商场banner
    system = db.Column(db.Integer, default=1)  # 1:运营后台注册, 2:司机端注册, 3:调度端
    note = db.Column(db.String(10))  # 备注
    up_time = db.Column(db.TIMESTAMP, default=datetime.now)  # 上架时间
    down_time = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 下架时间
    create_time = db.Column(db.TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间
