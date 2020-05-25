# -*- coding:utf-8 -*-
__author__ = "leimu"
__doc__ = "通用的定时任务组件"

import datetime
from flask import request, jsonify
from flask_apscheduler import APScheduler
from apscheduler.jobstores.redis import RedisJobStore
from .app import app
from .config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PWD

app.config['SCHEDULER_JOBSTORES'] = {
    'default': RedisJobStore(jobs_key='demo.apscheduler.jobs', run_times_key='demo.apscheduler.run_times',
                             db=REDIS_DB,
                             host=REDIS_HOST,
                             port=REDIS_PORT,
                             password=REDIS_PWD)
}

app.config['SCHEDULER_EXECUTORS'] = {
    'default': {'type': 'threadpool', 'max_workers': 20}
}


def alive():
    print("******i am alive!******")


app.config['SCHEDULER_API_ENABLED'] = True
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.add_job(id='keepalive', func=alive, args=(), trigger='interval', seconds=60, replace_existing=True)

scheduler.start()


def job1(a, b):
    print(str(a) + ' ' + str(b))


@app.route("/vx/job")
def add_job():
    a = scheduler.add_job(id="example0", func=job1, args=('循环任务', '-----------'), trigger='interval', seconds=3,
                          replace_existing=True)
    scheduler.add_job(id="example1", func=job1, args=('定时任务', '-----------'), trigger='cron', second='*/5')
    scheduler.add_job(id="example2", func=job1, args=('一次性任务', '-----------'),
                      next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=12),
                      replace_existing=True)
    # 在 2019-08-29 22:15:00至2019-08-29 22:17:00期间，每隔1分30秒 运行一次 job 方法
    scheduler.add_job(id="example3", func=job1, args=['阶段性循环任务', '-----------'], trigger='interval', minutes=1,
                      seconds=30, start_date='2019-08-29 22:15:00', end_date='2019-08-29 22:17:00')
    return jsonify({"job": str(a)})


@app.route("/vx/job", methods=['DELETE'])
def remove_job():
    job_id = request.values.get("id")
    a = scheduler.remove_job(id=job_id)

    return jsonify({"job": str(a)})


@app.route("/vx/job", methods=['PUT'])
def run_job():
    job_id = request.values.get("id")
    a = scheduler.run_job(id=job_id)
    return jsonify({"job": str(a)})


@app.route("/vx/jobs", methods=['GET'])
def get_all_jobs():
    a = scheduler.get_jobs()
    return jsonify({"job": str(a)})


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
