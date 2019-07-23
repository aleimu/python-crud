# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from route import cron_job_hour, cron_job_day
from cache import rds

show_key = "hour_show_{}".format  # 单条广告的曝光量的redis中的key
click_key = "hour_code_{}".format  # click_key = "code%s"
day_show_key = "day_show_{}".format  # 单条广告的日曝光量的redis中的key,按0-23小时段统计
day_click_key = "day_click_{}".format


# FLASK DEBUG模式下定时任务会执行两次
def aps_test():
    print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '你好')


defult_code = "5bc30530-ac41-11e9-9162-6c4b9029bde1"  # 自测


def show_count():
    """曝光计数"""
    print("one show", show_key(defult_code))
    rds.incr(show_key(defult_code))


def click_count():
    """点击计数"""
    print("one click", click_key(defult_code))
    rds.incr(click_key(defult_code))


scheduler = BackgroundScheduler()
scheduler.add_job(func=aps_test, trigger='cron', second='*/50')
scheduler.add_job(func=cron_job_hour, trigger='cron', minute='*/1')
scheduler.add_job(func=cron_job_day, trigger='cron', minute='*/2')
scheduler.add_job(func=show_count, trigger='cron', second='*/5')
scheduler.add_job(func=click_count, trigger='cron', second='*/15')

scheduler.start()

try:
    import uwsgi

    while True:
        sig = uwsgi.signal_wait()
        print(sig)
except Exception as err:
    pass

""" cron 参数
year (int 或 str)	年，4位数字
month (int 或 str)	月 (范围1-12)
day (int 或 str)	日 (范围1-31
week (int 或 str)	周 (范围1-53)
day_of_week (int 或 str)	周内第几天或者星期几 (范围0-6 或者 mon,tue,wed,thu,fri,sat,sun)
hour (int 或 str)	时 (范围0-23)
minute (int 或 str)	分 (范围0-59)
second (int 或 str)	秒 (范围0-59)
"""
