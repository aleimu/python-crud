# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"
__doc__ = "广告模块:1.广告图片和链接的管理 2.分组和归档 3.曝光量,点击量等统计"

import os
import time
import uuid
import traceback
from flask import send_from_directory, Blueprint, abort, json
from app import db, request, UPLOAD_FOLDER
from tools import constant as cs, validate_params, js, get_arg, all2dict, first2dict, values2db
from model import ad_style, ad_ctr, ad_group, ad_image
from cache import rds

advert = Blueprint('advert', __name__, url_prefix='/v1/advert')

show_key = "hour_show_{}".format  # 单条广告的曝光量的redis中的key
click_key = "hour_click_{}".format  # click_key = "code%s"
day_show_key = "day_show_{}".format  # 单条广告的日曝光量的redis中的key,按0-23小时段统计
day_click_key = "day_click_{}".format
group_dict = {'1': 'a_advert', '2': 'b_advert', '3': 'c_advert', '4': "d_advert"}


def allowed_file(filename):
    tail = '.' in filename and filename.rsplit('.', 1)[1]
    if tail.lower() in cs.ALLOWED_EXTENSIONS:
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
@advert.route('/upload/<string:filename>', methods=['GET'])
def uploaded_file(filename):
    if allowed_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        return js(cs.PARAM_ERR, None, None)


def rds_key(code):
    show = show_key(code)  # 单条广告的曝光量的redis中的key
    click = click_key(code)  # click_key = "code%s"
    day_show = day_show_key(code)  # 单条广告的日曝光量的redis中的key,按0-23小时段统计
    day_click = day_click_key(code)
    return show, click, day_show, day_click


@advert.route('/show')
def show_count():
    """曝光计数"""
    ad_code = request.values.get("code")
    rds.incr(show_key(ad_code))
    return js(cs.OK)


@advert.route('/click')
def click_count():
    """点击计数"""
    ad_code = request.values.get("code")
    rds.incr(click_key(ad_code))
    return js(cs.OK)


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
            group_obj = ad_group.query.filter(id=gid).first()
        else:
            group_obj = ad_group.query.filter().all()
        return js(cs.OK, None, all2dict(group_obj))
    if request.method == "PUT":
        if gid:
            group_obj = ad_group.query.filter_by(id=gid).first()
            if not group_obj:
                return js(cs.VALUE_ERROR, "分组不存在")
            group_check = ad_group.query.filter_by(group=gname).first()
            if group_check:
                return js(cs.VALUE_ERROR, "组名已存在")
            group_obj.group = gname
            group_obj.note = note
            db.session.add(group_obj)
        else:
            return js(cs.VALUE_ERROR)
    if request.method == "POST":
        if gname:
            group_obj = ad_group.query.filter_by(group=gname).first()
            if group_obj:
                return js(cs.VALUE_ERROR, "组名已存在")
            group_obj = values2db(req_arg, ad_group(), ("group", "note"))
            db.session.add(group_obj)
        else:
            return js(cs.VALUE_ERROR)
    if request.method == "DELETE":
        if gid:
            group_obj = ad_group.query.filter_by(id=gid).first()
            db.session.delete(group_obj)
        else:
            return js(cs.VALUE_ERROR)
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
    ad_url = req_arg.get('ad_url')  # 广告url
    note = req_arg.get('note')

    if request.method == "GET":
        if pid:
            img_obj = ad_image.query.filter_by(id=pid).first()
        else:
            img_obj = ad_image.query.filter().all()
        return js(cs.OK, None, all2dict(img_obj))
    elif request.method == "PUT":
        if pid:
            group_check = ad_group.query.filter_by(id=group_id).first()
            if not group_check:
                return js(cs.VALUE_ERROR, "组ID不存在")
            if ',' not in pid:
                img_obj = ad_image.query.filter_by(id=pid).first()
                if not img_obj:
                    return js(cs.VALUE_ERROR, "图片ID不存在")
                img_obj = values2db(req_arg, ad_image(), ("image_name", "image_url", "ad_url", "note", "group_id"))
                db.session.add(img_obj)
            else:
                pids = pid.split(',')  # 批量分组
                for item in pids:
                    img_obj = ad_image.query.filter_by(id=item).first()
                    if not img_obj:
                        return js(cs.VALUE_ERROR, "图片ID:%s不存在" % item)
                    img_obj.group_id = group_id
                    db.session.add(img_obj)
        else:
            return js(cs.VALUE_ERROR)
    elif request.method == "POST":
        group_check = ad_group.query.filter_by(id=group_id).first()
        if not group_check:
            return js(cs.VALUE_ERROR, "组ID不存在")
        img_obj = values2db(req_arg, ad_image(), ("image_name", "image_url", "ad_url", "note", "group_id"))
        db.session.add(img_obj)
    elif request.method == "DELETE":
        if pid:
            if ',' not in pid:
                img_obj = ad_image.query.filter_by(id=pid).first()
                if img_obj:
                    db.session.delete(img_obj)
            else:
                pids = pid.split(',')  # 批量删除
                for item in pids:
                    img_obj = ad_image.query.filter_by(id=item).first()
                    if img_obj:
                        db.session.delete(img_obj)
        else:
            return js(cs.VALUE_ERROR)
    db.session.commit()
    return js(cs.OK)


@advert.route('/style', methods=['GET'])
def get_ad_style():
    # 各端调用广告接口,查询可以展示的广告
    req_arg = get_arg()
    group_key = req_arg.get('system', "1")
    rds_key = group_dict.get(group_key)
    now_time = time.strftime('%Y-%m-%d %H:%M:%S')
    if not group_key:
        return js(cs.VALUE_ERROR, 'ad_key error', None)
    try:
        ad_dict = rds.get(rds_key)  # 尝试获取缓存
        if ad_dict:
            ad_dict = json.loads(ad_dict)
            for item in ad_dict:
                if item.get("down_time") < now_time:  # 删除失效广告缓存
                    raise Exception("%s Advert Expired" % rds_key)
        else:
            ad_dict = refresh(group_key)
            rds.set(rds_key, json.dumps(ad_dict))  # 加上缓存
    except Exception as e:
        print(traceback.format_exc())
        ad_dict = refresh(group_key)
        rds.set(rds_key, json.dumps(ad_dict))  # 加上缓存
    return js(cs.OK, None, ad_dict)


@advert.route('/style', methods=['POST', "PUT", "DELETE"])
def set_ad_style():
    """CRUD各端广告"""
    req_arg = get_arg()
    status = int(req_arg.get("status"))
    group_id = req_arg.get("group_id")
    image_id = req_arg.get("image_id")
    system = req_arg.get("system")
    if not req_arg:
        return js(cs.VALUE_ERROR)
    need = ("group_id", "image_id", "oper_uid", "oper_uname", "status", "close", "mode", "frequency",
            "position", "system", "note", "up_time", "down_time")
    if request.method == "POST":
        try:
            group_check = ad_group.query.filter_by(id=group_id).first()
            if not group_check:
                return js(cs.VALUE_ERROR, "组ID不存在")
            img_obj = ad_image.query.filter_by(id=image_id).first()
            if not img_obj:
                return js(cs.VALUE_ERROR, "图片ID不存在")
            img_obj = values2db(req_arg, ad_style(), need)
            code = str(uuid.uuid1())
            img_obj.code = code
            db.session.add(img_obj)
        except Exception as e:
            print(traceback.format_exc())
            return js(cs.DB_ERR, "内部错误")
    elif request.method == "PUT":
        try:
            ad_id = int(req_arg.get("id"))
            if not ad_id:
                return js(cs.VALUE_ERROR)
            group_check = ad_group.query.filter_by(id=group_id).first()
            if not group_check:
                return js(cs.VALUE_ERROR, "组ID不存在")
            img_obj = ad_image.query.filter_by(id=image_id).first()
            if not img_obj:
                return js(cs.VALUE_ERROR, "图片ID不存在")
            style_obj = ad_style.query.filter_by(id=ad_id).first()
            code = style_obj.code
            img_obj = values2db(req_arg, style_obj, need)
            db.session.add(img_obj)
        except Exception as e:
            print(traceback.format_exc())
            return js(cs.DB_ERR, "内部错误")
    elif request.method == "DELETE":
        try:
            ad_id = int(req_arg.get("id"))
            if not ad_id:
                return js(cs.VALUE_ERROR)
            style_obj = ad_style.query.filter_by(id=ad_id).first()
            code = style_obj.code
            db.session.delete(style_obj)
        except Exception as e:
            print(traceback.format_exc())
            return js(cs.DB_ERR, "内部错误")
    else:
        return js(cs.VALUE_ERROR)
    sync2redis(code, status)
    db.session.commit()
    return js(cs.OK)


def check_position():
    """检查 系统版位占用情况"""
    pass


@advert.route('/list', methods=['GET'])
def ad_list():
    """广告汇总列表展示"""
    req_arg = get_arg()
    status = req_arg.get("status")
    group_id = req_arg.get("group_id")
    image_id = req_arg.get("image_id")
    system = req_arg.get("system")
    position = req_arg.get("position")
    page_index = req_arg.get('page_index')
    page_size = req_arg.get('page_size')
    if not page_index or not page_size:
        page_index = 1
        page_size = 20
    try:
        ad_obj = db.session.query(ad_style.id, ad_style.code, ad_style.mode, ad_style.frequency, ad_style.position,
                                  ad_style.system, ad_image.image_name, ad_image.image_url, ad_image.ad_url,
                                  ad_image.group_id, ad_style.up_time, ad_style.down_time, ad_style.status,
                                  ad_style.node) \
            .join(ad_image, ad_image.id == ad_style.image_id).filter()
        if status:
            ad_obj = ad_obj.filter(ad_style.status == status)
        if system:
            ad_obj = ad_obj.filter(ad_style.system == system)
        if position:
            ad_obj = ad_obj.filter(ad_style.position == position)
        if image_id:
            ad_obj = ad_obj.filter(ad_style.image_id == image_id)
        if group_id:
            ad_obj = ad_obj.filter(ad_style.image_id == group_id)
        ad_obj = ad_obj.paginate(int(page_index), int(page_size), False)
        count = ad_obj.total
        data = all2dict(ad_obj.items)
        return js(cs.OK, None, {"count": count, "data": data})
    except Exception as e:
        print(traceback.format_exc())
        return js(cs.DB_ERR)


@advert.route('/statistic', methods=['GET'])
def statistic():
    """多条广告展示量/点击量汇总列表展示"""
    req_arg = get_arg()
    code = req_arg.get("code")
    start_date = req_arg.get("start_date")
    end_date = req_arg.get("end_date")
    page_index = req_arg.get('page_index')
    page_size = req_arg.get('page_size')
    sort = req_arg.get("sort")  # 图与表排序不一样
    if not page_index or not page_size:
        page_index = 1
        page_size = 20
    try:
        ad_obj = db.session.query(ad_ctr.code, ad_ctr.show_count, ad_ctr.click_count, ad_ctr.crt,
                                  ad_ctr.show_day, ad_ctr.click_day, ad_ctr.create_date, ad_ctr.create_time).filter()
        if code:
            ad_obj = ad_obj.filter(ad_ctr.code.in_(code.split(',')))
        if sort:
            ad_obj = ad_obj.order_by(ad_ctr.create_date.desc())
        else:
            ad_obj = ad_obj.order_by(ad_ctr.create_date)
        if not start_date:
            start_date = time.strftime('%Y-%m-%d %H:%M:%S')
        if not end_date:
            end_date = time.strftime('%Y-%m-%d %H:%M:%S')
        ad_obj = ad_obj.filter(ad_ctr.create_date <= end_date, ad_ctr.create_date >= start_date).paginate(
            int(page_index), int(page_size), False)
        count = ad_obj.total
        data = all2dict(ad_obj.items)
        return js(cs.OK, None, {"count": count, "data": data})
    except Exception as e:
        print(traceback.format_exc())
        return js(cs.DB_ERR)


def sync2redis(code, status):
    """对广告的改删同步到redis ;status: 0：已下架 1：已上架 2:暂存未发布 3:已删除弃用"""
    if status == 0:
        settle_expired(code)
    if status == 1:
        daily_init(code)
    if status == 2:
        pass
    if status == 3:
        clean_expired(code)


def daily_init(code):
    # 初始化当天redis中全部的记录
    show_key, click_key, dshow_key, dclick_key = rds_key(code)
    daily_statistics = {x: 0 for x in range(24)}  # 初始化一天内的每小时点击量统计
    rds.delete(show_key, click_key, dshow_key, dclick_key)
    rds.hmset(dshow_key, daily_statistics)
    rds.hmset(dclick_key, daily_statistics)


def merge_rds(code):
    """将单条广告的曝光量/点击量 依据小时划分,同步到日曝光量/日点击量对应时段下"""

    show_key, click_key, dshow_key, dclick_key = rds_key(code)
    hour = time.localtime().tm_hour
    show_count = rds.get(show_key)
    click_count = rds.get(click_key)
    rds.delete(show_key, click_key)
    if not show_count:
        show_count = 0
    if not click_count:
        click_count = 0
    redis_show_count = rds.hget(dshow_key, hour)
    redis_click_count = rds.hget(dclick_key, hour)
    if not redis_show_count:
        redis_show_count = 0
    if not redis_click_count:
        redis_click_count = 0
    if not any([redis_click_count, redis_show_count]):  # 检查是否已提交过 FIXME
        daily_init(code)
    now_show_count = rds.hset(dshow_key, hour, int(redis_show_count) + int(show_count))
    now_click_count = rds.hset(dclick_key, hour, int(redis_click_count) + int(click_count))
    return now_show_count, now_click_count


def merge_db(code):
    """将单条广告的日曝光量/日点击量/时段统计同步到mysql"""
    daily_show = rds.hgetall(day_show_key(code))
    daily_click = rds.hgetall(day_click_key(code))
    now_date = time.strftime('%Y-%m-%d')  # 按天统计
    scout = sum([int(x) for x in daily_show.values()])
    ccout = sum([int(x) for x in daily_click.values()])
    if scout:
        crt = float(ccout) / float(scout)
    else:
        crt = 0
    try:
        ad_ctr_obj = db.session.query(ad_ctr).filter(ad_ctr.code == code, ad_ctr.create_date == now_date).first()
        if not ad_ctr_obj:
            new_ctr = ad_ctr(code=code, create_date=now_date, crt=crt, show_count=scout, click_count=ccout,
                             show_day=json.dumps(daily_show), click_day=json.dumps(daily_click))
            db.session.add(new_ctr)
        else:
            ad_ctr_obj.show_count = scout
            ad_ctr_obj.click_count = ccout
            ad_ctr_obj.crt = crt
            ad_ctr_obj.show_day = json.dumps(daily_show)
            ad_ctr_obj.click_day = json.dumps(daily_click)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())


def refresh(system=None, status=1):
    """依据系统id,返回所有此系统的最新广告列表"""
    ad_lists = []
    try:
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        ad_obj = db.session.query(ad_style.id, ad_style.code, ad_style.mode, ad_style.frequency, ad_style.position,
                                  ad_style.system, ad_image.image_name, ad_image.image_url, ad_image.ad_url,
                                  ad_style.up_time, ad_style.down_time) \
            .join(ad_image, ad_image.id == ad_style.image_id) \
            .filter(ad_style.status == status)
        if system:
            ad_obj = ad_obj.filter(ad_style.system == system)
        if now_time:
            ad_obj = ad_obj.filter(ad_style.up_time <= now_time, ad_style.down_time >= now_time)
        ad_obj = ad_obj.all()
        db.session.commit()
        if not ad_obj:
            abort(406, "not find:%s" % system)
        ad_lists = all2dict(ad_obj)
        return ad_lists
    except Exception as e:
        db.session.remove()
        print(traceback.format_exc())
        return ad_lists


def check_expired(cycle=False):  # cycle=False 小时周期,cycle=True 天周期
    """检查单个系统的广告过期情况,刷新数库最新广告进入redis缓存"""
    now_time = time.strftime('%Y-%m-%d %H:%M:%S')
    for system in group_dict.keys():
        system_key = group_dict.get(system)
        ad_dict_old = rds.get(system_key)  # 获取缓存中的广告
        ad_dict_new = refresh(system)  # 获取当前最新的广告
        if ad_dict_old:
            ad_dict = json.loads(ad_dict_old)
            for item in ad_dict:
                try:
                    code = item.get("code")
                    if item.get("down_time") < now_time:  # 删除失效广告缓存
                        settle_expired(code)
                    else:
                        merge_rds(code)
                        if cycle:
                            merge_db(code)
                            daily_init(code)
                except Exception as e:
                    print(traceback.format_exc())
        rds.set(system_key, json.dumps(ad_dict_new))  # 加上缓存


def settle_expired(code):
    """清算过期的广告近期的点击量等,并删除缓存key"""
    merge_rds(code)
    merge_db(code)
    clean_expired(code)


def clean_expired(code):
    show_key, click_key, dshow_key, dclick_key = rds_key(code)
    rds.delete(show_key, click_key, dshow_key, dclick_key)


#########################################################内部接口#######################################################

@advert.route('/hour')
def cron_job_hour():
    """按小数刷新redis数据到按天统计中"""
    print("-----------cron_job_hour---------------")
    check_expired(False)
    return js(cs.OK)


@advert.route('/day')
def cron_job_day():
    """按天刷新redis中数据到db中"""
    print("-----------cron_job_day---------------")
    check_expired(True)
    return js(cs.OK)


@advert.route('/fresh')
def cron_job_fresh():
    """重置redis中的key"""
    print("-----------cron_job_fresh---------------")
    ad_dict = refresh()
    for item in ad_dict:
        code = item.get("code")
        if code:
            daily_init(code)
    return js(cs.OK)


@advert.route('/init')
def cron_job_init():
    """删除缓存,获取最新的广告信息"""
    print("-----------cron_job_init---------------")
    rds.delete(group_dict.values())
    return js(cs.OK)
