# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-07-07"
__doc__ = "运单列表查询"

import traceback
from datetime import datetime
from app import db, logger
from sqlalchemy import text, alias, and_, or_, distinct
from sqlalchemy.orm import aliased
from tools.common import all2dict, first2dict
from cache import cached, LRUCache
from model import User, TableA, TableB, TableC, TableD, TableE, TableF

TableD2 = aliased(TableD)


@cached(cache=LRUCache(maxsize=300))
def location_name(code):
    try:
        if code:
            TableB_obj = TableB.query.filter(TableB.code == code).with_entities(TableB.name).first()
            if TableB_obj:
                return TableB_obj.name
    except Exception as e:
        logger.error("location_name catch error: %s" % traceback.format_exc())
        return None


def export_trans(product_no, start_name, end_name, plate, start_date, end_date, mobile, price_no, waybill_status):
    """A与无缝对接运单导出"""
    no_data = []
    err, search_sql_obj = common_trans_list(product_no, start_name, end_name, plate, start_date, end_date, mobile,
                                            price_no, waybill_status, no_data)
    if err:
        return err, None
    if isinstance(search_sql_obj, dict):
        return None, search_sql_obj
    trans = search_sql_obj.order_by(TableC.create_time.desc()).all()
    trans_list = []
    trans_status_dict = {200: u"待接单", 201: u"待签到", 202: u"绑定头", 203: u"未绑定头",
                         300: u"待装", 301: u"已废止", 302: u"无效运单",
                         500: u"运输中", 501: u"已完成", 502: u"人工完成", 503: u"异常待确认"}
    execl_header = [u'运单号', u'签号', u'编号号', u'线路名称', u'运单属性', u'运单状态', u'店铺名称', u'司机姓名',
                    u'司机手机号', u'创建时间', u'实际发时间', u'实际到时间']
    is_overtime_dict = {0: u'正班', 1: u'加班'}
    trans_list.append(execl_header)
    for item in trans:
        tran = ["", "", "", "", "", "", "", "", "", "", "", "", ""]
        try:  # 补全关联表数据
            tran[0] = item.product_no
            tran[1] = item.price_no
            tran[2] = item.plate
            tran[3] = item.line_name
            tran[4] = is_overtime_dict.get(item.is_overtime, u"")
            tran[5] = trans_status_dict.get(item.status, u"")
            tran[6] = item.shop_name
            tran[7] = item.driver_name
            tran[8] = item.driver_tel
            tran[9] = item.create_time
            tran[10] = item.status_time  # 实际发时间
            tran[11] = item.status_time2  # 实际到时间
        except Exception as e:
            logger.error(traceback.format_exc())
        trans_list.append(tran)
    db.session.remove()
    return None, trans_list


def list_trans(product_no, start_name, end_name, plate, start_date, end_date, mobile, price_no, waybill_status,
               page, per_page):
    """A与无缝对接运单查询"""
    no_data = {"count": 0, "trans": []}
    err, search_sql_obj = common_trans_list(product_no, start_name, end_name, plate, start_date, end_date, mobile,
                                            price_no, waybill_status, no_data)
    if err:
        return err, None
    if isinstance(search_sql_obj, dict):
        return None, search_sql_obj
    trans = search_sql_obj.order_by(TableC.create_time.desc()).paginate(int(page), int(per_page), False)
    count = trans.total
    trans_list = []
    is_overtime_dict = {0: u'正班', 1: u'加班'}
    for item in trans.items:
        try:  # 补全关联表数据
            tran = first2dict(item)
            tran['create_date'] = datetime.strftime(item.create_time, '%Y-%m-%d')
            tran['is_overtime'] = is_overtime_dict.get(item.is_overtime, u"")
            if item.fk_at_location_code:
                tran['fk_at_location_name'] = location_name(item.fk_at_location_code)
            if item.fk_to_location_code:
                tran['fk_to_location_name'] = location_name(item.fk_to_location_code)
            trans_list.append(tran)
        except Exception as e:
            logger.error(traceback.format_exc())
    trans_info = {"count": count, "trans": trans_list}
    db.session.remove()
    return None, trans_info


# 通用sql
def common_trans_list(product_no, start_name, end_name, plate, start_date, end_date, mobile, price_no,
                      waybill_status, no_data=()):
    search_sql = db.session.query(TableC.product_no, TableC.create_time, TableC.is_overtime, TableC.plate, TableC.fk_to_location_code,
                                  TableC.fk_at_location_code, TableC.line_no, TableC.shop_name, TableC.status, TableC.trailer_head,
                                  User.fullname.label("driver_name"), User.telephone.label("driver_tel"),
                                  TableD.status_time, TableD2.status_time.label("status_time2"),
                                  TableA.line_name, rct.price_no) \
        .join(rct, rct.product_no == TableC.product_no) \
        .join(TableA, TableA.line_no == TableC.line_no) \
        .join(TableD, and_(TableD.product_no == TableC.product_no, TableD.fk_location_code == TableC.fk_at_location_code,
                         TableD.type == 2), isouter=True) \
        .join(TableD2, and_(TableD2.product_no == TableC.product_no, TableD2.fk_location_code == TableC.fk_to_location_code,
                          TableD2.type == 1), isouter=True) \
        .join(Driver, Driver.id == TableC.fk_driver_id, isouter=True) \
        .join(User, User.id == Driver.user_id, isouter=True) \
        .distinct()
    if waybill_status:
        if int(waybill_status) == 210:
            search_sql = search_sql.filter(and_(TableC.status == 200, or_(TableC.fk_driver_id == None, TableC.fk_driver_id == 0)))
        elif int(waybill_status) == 211:
            search_sql = search_sql.filter(and_(TableC.status == 200, TableC.fk_driver_id != None, TableC.fk_driver_id == 0))
        elif int(waybill_status) == 212:
            search_sql = search_sql.filter(TableC.status.in_(201, 300))
        else:
            search_sql = search_sql.filter(TableC.status == waybill_status)
    if product_no:
        search_sql = search_sql.filter(TableC.product_no == product_no)
    elif price_no:
        trans = db.session.query(rct.product_no).filter_by(price_no=price_no).all()
        if trans:
            search_sql = search_sql.filter(TableC.product_no.in_(trans))
        else:
            return None, no_data
    if plate:
        search_sql = search_sql.filter(or_(TableC.plate == plate, TableC.trailer_head == plate))  # 查头编号和厢编号都可以
    if mobile:
        user = User.query.filter(User.telephone == mobile).first()
        if user:
            driver = Driver.query.filter(Driver.user_id == user.id).first()
            if driver:
                search_sql = search_sql.filter(TableC.fk_driver_id == driver.id)
            else:
                return None, no_data
        else:
            return None, no_data
    if start_date:
        search_sql = search_sql.filter(TableC.create_time > start_date + ' 00:00:00')
    if end_date:
        search_sql = search_sql.filter(TableC.create_time < end_date + ' 23:59:59')
    if start_name:
        start = TableB.query.filter(TableB.name.like('%' + start_name + '%')).with_entities(TableB.code).all()
        if start:
            search_sql = search_sql.filter(TableC.fk_at_location_code.in_([x[0] for x in start]))
    if end_name:
        end = TableB.query.filter(TableB.name.like('%' + end_name + '%')).with_entities(TableB.code).all()
        if end:
            search_sql = search_sql.filter(TableC.fk_to_location_code.in_([x[0] for x in end]))
    return None, search_sql
