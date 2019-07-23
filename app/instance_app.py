# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

import traceback
import sqlalchemy.exc
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
import flask_excel as excel
from .config import *
from .logger import logger
from tools import APIEncoder, js, SERVER_ERR, DB_ERR, AUTH_FAIL, PARAM_ERR, OK

app = Flask(__name__)
app.config['DEBUG'] = DEBUG
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY

app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['DATABASE_QUERY_TIMEOUT'] = DATABASE_QUERY_TIMEOUT  # 配置查询超时时间
app.config['SQLALCHEMY_RECORD_QUERIES'] = SQLALCHEMY_RECORD_QUERIES  # 保存查询记录
app.json_encoder = APIEncoder  # 直接修改json对时间/sqlalchemy obj的解析方式

db = SQLAlchemy(app)
excel.init_excel(app)


@app.before_request
def before_request():
    logger.info('url: %s ,data: %s' % (request.path, request.values.to_dict()), extra={"type": request.method})
    # if request.path in NOT_AUTH_API or (request.path.split('.')[-1] in ALLOWED_EXTENSIONS):
    #     pass
    # else:
    #     token = request.values.get('token', None)
    #     if not token:
    #         if request.json:
    #             token = request.json.get('token', None)
    #     if token:
    #         user = rds.hgetall(key_token(token))
    #         if not user:
    #             return js(AUTH_FAIL, "TOKEN_ERR", None)
    #         rds.expire(key_token(token), LOGIN_EXPIRE)
    #     else:
    #         return js(AUTH_FAIL, "TOKEN_ERR", None)


@app.after_request
def after_request(response):
    if "export" in request.path or "export" in request.args.get("flag", ""):  # 以数据流形式下载文件
        response.headers["Content-type"] = 'application/octet-stream'
    for query in get_debug_queries():
        # 如果超出查询时间,会将具体的函数,行号,sql语句记录到日志之中
        if query.duration > app.config['DATABASE_QUERY_TIMEOUT']:
            logger.warning('Context:{} SLOW QUERY: {} Parameters: {} Duration: {}'
                           .format(query.context, query.statement, query.parameters, query.duration))
    return response


@app.teardown_request
def teardown_request(response):
    db.session.remove()


@app.errorhandler(401)
def auth_err(e):
    logger.error(traceback.format_exc(), extra={"key": e.__class__})
    return js(AUTH_FAIL, "TOKEN_ERR", None)


@app.errorhandler(405)
def param_err(e):
    return js(PARAM_ERR, str(e), None)


@app.errorhandler(406)
def obj_not_find(e):
    return js(OK, str(e), None)


@app.errorhandler(500)
def server_err(e):
    logger.error(traceback.format_exc(), extra={"key": e.__class__})
    return js(SERVER_ERR, "SERVER_ERR", None)


@app.errorhandler(sqlalchemy.exc.DBAPIError)
def db_err(e):
    logger.error(traceback.format_exc(), extra={"key": e.__class__})
    db.session.rollback()
    return js(DB_ERR, "DB_ERR", None)


@app.errorhandler(Exception)
def unhandled_exception(e):
    logger.error(traceback.format_exc(), extra={"key": e.__class__})
    return js(SERVER_ERR, "SERVER_ERR", None)
