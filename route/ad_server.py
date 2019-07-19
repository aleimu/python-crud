# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"
__doc__ = "广告模块:1.广告图片和链接的管理 2.分组和归档 3.曝光量,点击量等统计"

import os
import time
import json
import uuid
import traceback
from datetime import datetime
from flask import send_from_directory, Blueprint, abort
from sqlalchemy import and_
from app import db, request, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, DATA_FOLDER
from tools import constant as cs, validate_params, js, get_arg, all2dict, first2dict, values2db
from model import ad_style, ad_ctr, ad_group, ad_image
from cache import rds, key_token

advert = Blueprint('advert', __name__, url_prefix='/v1/advert')

big_flag = "dispatch_image_740_102"
small_flag = "dispatch_image_378_102"
local_flag = UPLOAD_FOLDER + "/dispatch_image_local_file.txt"  # 存储路径名和对应url的本地文件


def allowed_file(filename):
    tail = '.' in filename and filename.rsplit('.', 1)[1]
    if tail.lower() in ALLOWED_EXTENSIONS:
        return tail
    else:
        return False


@advert.route('/upload', methods=['POST'])  # 上传文件,并返回此文件的链接
@validate_params(required=['username'])
def upload_file():
    name = request.values.get('filename')
    group = request.values.get('group')
    file = request.files['file']
    tail = allowed_file(file.filename)
    if file and tail:
        now = int(time.time())
        filename = name + '_' + group + '_' + str(now) + '.%s' % tail
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return js(cs.OK, None, filename)
    else:
        return js(cs.FILE_ILLEGAL, None, {})


@advert.route('/<string:filename>', methods=['GET'])  # 访问图片
@advert.route('/uploaded/<string:filename>', methods=['GET'])
def uploaded_file(filename):
    if allowed_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        return js(cs.PARAM_ERR, None, None)


@advert.route('/group', methods=['POST', 'GET', "PUT", "DELETE"])
def crud_group():
    """分组的CRUD"""
    req_arg = get_arg()
    gid = req_arg.get('id')
    gname = req_arg.get('group')
    note = req_arg.get('note')

    if request.method == "GET":
        if gid:
            # group_obj = ad_group.query.filter_by(id=id).first()
            group_obj = ad_group.to_first(id=gid)
        else:
            group_obj = ad_group.query.filter().all()
        return js(cs.OK, None, all2dict(group_obj))
    if request.method == "PUT":
        if gid:
            group_obj = ad_group.query.filter_by(id=gid).first()
            if not group_obj:
                return js(cs.PARAM_ERR, "分组不存在")
            group_check = ad_group.query.filter_by(group=gname).first()
            if group_check:
                return js(cs.PARAM_ERR, "组名已存在")
            group_obj.group = gname
            group_obj.note = note
            db.session.add(group_obj)
        else:
            return js(cs.PARAM_ERR)
    if request.method == "POST":
        if gname:
            group_obj = ad_group.query.filter_by(group=gname).first()
            if group_obj:
                return js(cs.PARAM_ERR, "组名已存在")
            group_obj = values2db(req_arg, ad_group(), ("group", "note"))
            db.session.add(group_obj)
        else:
            return js(cs.PARAM_ERR)
    if request.method == "DELETE":
        if gid:
            group_obj = ad_group.query.filter_by(id=gid).first()
            db.session.delete(group_obj)
        else:
            return js(cs.PARAM_ERR)
    db.session.commit()
    return js(cs.OK)


@advert.route('/image', methods=['POST', 'GET', "PUT", "DELETE"])
def crud_image():
    """图片的CRUD"""
    req_arg = get_arg()
    pid = req_arg.get('id')  # 图片id
    group_id = req_arg.get('group_id')  # 分组id
    image_name = req_arg.get('image_name')  # 图片自定义名称
    image_url = req_arg.get('image_url')  # 图片存储url
    note = req_arg.get('note')

    if request.method == "GET":
        if pid:
            img_obj = ad_image.query.filter_by(id=pid).first()
        else:
            img_obj = ad_image.query.filter.all()
        return all2dict(img_obj)
    elif request.method == "PUT":
        if pid:
            img_obj = ad_image.query.filter_by(id=pid).first()
            if not img_obj:
                return js(cs.PARAM_ERR, "图片ID不存在")
            group_check = ad_group.query.filter_by(id=group_id).first()
            if not group_check:
                return js(cs.PARAM_ERR, "组ID不存在")
            img_obj = values2db(req_arg, ad_image(), ("image_name", "image_url", "note", "group_id"))
            db.session.add(img_obj)
        else:
            return js(cs.PARAM_ERR)
    elif request.method == "POST":
        img_obj = values2db(req_arg, ad_image(), ("image_name", "image_url", "note", "group_id"))
        db.session.add(img_obj)
    elif request.method == "DELETE":
        if pid:
            img_obj = ad_image.query.filter_by(id=pid).first()
            db.session.delete(img_obj)
        else:
            return js(cs.PARAM_ERR)
    db.session.commit()
    return js(cs.OK)


@advert.route('/style', methods=['GET'])
def get_ad_style():
    # 各端调用广告接口,查询可以展示的广告
    req_arg = get_arg()
    ad_key = req_arg.get('ad_key', 'dispatch')
    # now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now_time = time.strftime('%Y-%m-%d %H:%M:%S')
    if not ad_key:
        return js(cs.PARAM_ERR, 'ad_key error', None)
    try:
        ad_dict = rds.hgetall(ad_key)  # 尝试获取缓存
        if ad_dict:
            if ad_dict.get("down_time") < int(now_time):  # 删除失效广告
                rds.delete(ad_key)
                ad_dict = get_refresh(ad_key, now_time)
        else:
            ad_dict = get_refresh(ad_key, now_time)
            rds.hmset(ad_key, ad_dict)  # 加上缓存
    except Exception as e:
        print(traceback.format_exc())
        ad_dict = get_refresh(ad_key, now_time)
        rds.hmset(ad_key, ad_dict)  # 加上缓存
    return js(cs.OK, None, ad_dict)


@advert.route('/style', methods=['POST', "PUT", "DELETE"])
def set_ad_style():
    """CRUD各端广告"""
    req_arg = get_arg()
    status = req_arg.get("status")
    if not req_arg:
        return js(cs.PARAM_ERR)
    need = ("group_id", "image_id", "oper_uid", "oper_uname", "status", "close", "mode", "frequency",
            "position", "system", "note", "up_time", "down_time")
    if request.methods == "POST":
        try:
            img_obj = values2db(req_arg, ad_style(), need)
            code = str(uuid.uuid1())
            img_obj.code = code
            db.session.add(img_obj)
        except Exception as e:
            print(traceback.format_exc())
            return js(cs.DB_ERR, "内部错误")
    elif request.methods == "PUT":
        try:
            ad_id = int(req_arg.get("id"))
            if not ad_id:
                return js(cs.PARAM_ERR)
            style_obj = ad_style.first(ad_id)
            code = style_obj.code
            img_obj = values2db(req_arg, style_obj, need)
            db.session.add(img_obj)
        except Exception as e:
            print(traceback.format_exc())
            return js(cs.DB_ERR, "内部错误")
    elif request.methods == "DELETE":
        try:
            ad_id = int(req_arg.get("id"))
            if not ad_id:
                return js(cs.PARAM_ERR)
            style_obj = ad_style.first(ad_id)
            code = style_obj.code
            db.session.delete(style_obj)
        except Exception as e:
            print(traceback.format_exc())
            return js(cs.DB_ERR, "内部错误")
    else:
        return js(cs.PARAM_ERR)
    sync2redis(code, status)
    db.session.commit()
    return js(cs.OK)


show_key = "hour_show_{}".format  # 单条广告的曝光量的redis中的key
click_key = "hour_code_{}".format  # click_key = "code%s"
day_show_key = "day_show_{}".format  # 单条广告的日曝光量的redis中的key,按0-23小时段统计
day_click_key = "day_click_{}".format


def sync2redis(code, status):
    """对广告的改删同步到redis ;status: 0：已下架 1：已上架 2:暂存未发布 3:已删除弃用"""
    show_code = show_key(code)
    click_code = click_key(code)
    dshow_key = day_show_key(code)
    dclick_key = day_click_key(code)
    if status == 0:
        merge_count(code)
        dss = rds.hgetall(dshow_key)
        dsc = rds.hgetall(dclick_key)
        sync2db(code, dss, dsc)  # 下架后清空当天redis中全部的记录
        rds.delete(show_code, click_code, dshow_key, dclick_key)
    if status == 1:
        daily_statistics = {x: 0 for x in range(24)}  # 初始化一天内的每小时点击量统计
        rds.delete(dshow_key, dclick_key)
        rds.hset(dshow_key, daily_statistics)
        rds.hset(dclick_key, daily_statistics)
    if status == 2:
        pass
    if status == 3:
        rds.delete(show_code, click_code, dshow_key, dclick_key)


def merge_count(code):
    """将单条广告的曝光量/点击量 依据小时划分,同步到日曝光量/日点击量对应时段下"""
    dshow_key = day_show_key(code)
    dclick_key = day_click_key(code)
    show_count = rds.get(show_key(code))
    click_count = rds.get(click_key(code))
    hour = time.localtime().tm_hour
    redis_show_count = rds.hget(dshow_key, hour)
    redis_click_count = rds.hget(dclick_key, hour)
    # 检查是否已提交过 FIXME
    now_show_count = rds.hset(dshow_key, int(redis_show_count) + int(show_count))
    now_click_count = rds.hset(dclick_key, int(redis_click_count) + int(click_count))
    return now_show_count, now_click_count


def sync2db(code, daily_stat_show, daily_stat_click):
    """将单条广告的日曝光量/日点击量/时段统计同步到mysql"""
    now_date = time.strftime('%Y-%m-%d')

    db.session.query(ad_ctr).filter(ad_ctr.code == code, ad_ctr.create_date == now_date).update(
        {"show_count": sum([int(x) for x in daily_stat_show.values()]),
         "click_count": sum([int(x) for x in daily_stat_click.values()]),
         "show_day": json.dumps(daily_stat_show),
         "click_day": json.dumps(daily_stat_click)})


def merge(count, day_statist):
    pass


# storage
def sum_count(code):
    pass


def sum_all(code):
    pass


def get_refresh(ad_key, now_time, status=1):
    """依据系统id,返回所有此系统的最新广告列表"""
    ad_obj = db.session.query(ad_style.code, ad_style.mode, ad_style.frequency, ad_style.position,
                              ad_style.system, ad_image.image_name, ad_image.image_url, ad_style.up_time,
                              ad_style.down_time).join(ad_image, ad_image.id == ad_style.image_id)
    if ad_key:
        ad_obj = ad_obj.filter(ad_style.system == ad_key, ad_style.status == status)
    if now_time:
        ad_obj = ad_obj.filter(ad_style.up_time <= now_time, ad_style.down_time >= now_time)
    ad_obj = ad_obj.all()
    if not ad_obj:
        abort(406)
    ad_dict = all2dict(ad_obj)
    return ad_dict


@advert.route('/show')
def show_count():
    """曝光计数"""
    ad_code = request.vlues.get("code")
    rds.incr("show" + ad_code)
    return js(cs.OK)


@advert.route('/click')
def click_count():
    """点击计数"""
    ad_code = request.vlues.get("code")
    rds.incr("click" + ad_code)
    return js(cs.OK)
