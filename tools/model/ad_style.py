# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from .base import *
from .ad_group import AdGroup, AdGroup2
from .ad_image import AdImage, AdImage2
from .user import User, User2


class AdStyle(Base):  # 广告展示方式与设置
    __tablename__ = 'ad_style'
    __bind_key__ = db.get("read_db")

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False)  # 广告编号-> redis key
    group_id = Column(Integer, ForeignKey('{}.ad_group.id'.format(db.read_db)), index=True)  # 分组id :AdGroup.id
    image_id = Column(Integer, ForeignKey('{}.ad_image.id'.format(db.read_db)))  # 图片id ->AdImage.id
    oper_uid = Column(Integer, ForeignKey('{}.user.id'.format(db.read_db)))  # 操作人id;user.id
    oper_uname = Column(String(11))  # 操作人username
    ad_url = Column(String(256))  # 广告链接
    status = Column(Integer, default=2)  # 状态(0：已下架 1：已上架 2:暂存未发布 3:已删除弃用)  -> 同一个位置只能上架一个产品和图片展示方式有关
    close = Column(Integer, default=0)  # 是否可点击关闭(0：可关闭；1：不可关闭 )
    mode = Column(Integer, default=0)  # 图片展示方式: 轮播,横幅
    frequency = Column(String(5), default=0.5)  # 图片轮播的频率0.1-0.5s
    position = Column(String(5), default=1)  # 图片摆放位置: 1:首页banner,2:首页底部,3:商场banner
    system = Column(Integer, default=1)  # 1: 系统1, 2:系统2, 3:系统3, 4: 系统4
    note = Column(String(32))  # 备注
    up_time = Column(TIMESTAMP, default=datetime.now)  # 上架时间
    down_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 下架时间
    create_time = Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间

    # group = db.relationship("AdGroup", uselist=False, foreign_keys=[group_id])
    # image = db.relationship("AdImage", uselist=False, foreign_keys=[image_id])
    # user = db.relationship("User", uselist=False, foreign_keys=[oper_uid])


class AdStyle2(Base):  # 广告展示方式与设置
    __tablename__ = 'ad_style'
    __bind_key__ = db.get("write_db")
    __table_args__ = {
        'schema': db.get("write_db"),
        "extend_existing": True
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False)  # 广告编号-> redis key
    group_id = Column(Integer, ForeignKey('{}.ad_group.id'.format(db.write_db)), index=True)  # 分组id :AdGroup.id
    image_id = Column(Integer, ForeignKey('{}.ad_image.id'.format(db.write_db)))  # 图片id ->AdImage.id
    oper_uid = Column(Integer, ForeignKey('{}.user.id'.format(db.write_db)))  # 操作人id;user.id
    oper_uname = Column(String(11))  # 操作人username
    ad_url = Column(String(256))  # 广告链接
    status = Column(Integer, default=2)  # 状态(0：已下架 1：已上架 2:暂存未发布 3:已删除弃用)  -> 同一个位置只能上架一个产品和图片展示方式有关
    close = Column(Integer, default=0)  # 是否可点击关闭(0：可关闭；1：不可关闭 )
    mode = Column(Integer, default=0)  # 图片展示方式: 轮播,横幅
    frequency = Column(String(5), default=0.5)  # 图片轮播的频率0.1-0.5s
    position = Column(String(5), default=1)  # 图片摆放位置: 1:首页banner,2:首页底部,3:商场banner
    system = Column(Integer, default=1)  # 1: 系统1, 2:系统2, 3:系统3, 4: 系统4
    note = Column(String(32))  # 备注
    up_time = Column(TIMESTAMP, default=datetime.now)  # 上架时间
    down_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 下架时间
    create_time = Column(TIMESTAMP, default=datetime.now)  # 提交时间
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)  # 更新时间

    # group = db.relationship("AdGroup2", uselist=False, foreign_keys=[group_id])
    # image = db.relationship("AdImage2", uselist=False, foreign_keys=[image_id])
    # user = db.relationship("User2", uselist=False, foreign_keys=[oper_uid])
