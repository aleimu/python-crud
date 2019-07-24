# Python Fast CRUD

https://github.com/aleimu/python-crud

## 目的

本项目采用了一系列Python中比较流行的组件，可以以本项目为基础快速搭建Restful Web API, 这里主要是放了一些常用的CRUD操作示例和自己积累的通用函数.

## 特色

本项目使用了下面的常用组件：

1. [Flask](https://github.com/pallets/flask): 轻量级Web框架，可以说是Python中最易用的了 
2. [Flask-SQLAlchemy](https://github.com/pallets/flask-sqlalchemy): ORM工具。本项目需要配合Mysql使用,sqlalchemy的flask包装,更易使用
3. [Redis](https://github.com/andymccurdy/redis-py): Python Redis客户端
4. 本项目是使用token验证

本项目已经预先实现了一些常用的代码方便参考和复用:

1. 创建了用户模型
2. 实现了```/v1/user/register```用户注册接口
3. 实现了```/v1/user/login```用户登录接口
4. 实现了```/v1/user/logout```用户登出接口(需要登录后获取token)
5. 图片分组的CRUD
6. 图片的展示策略的CRUD
7. 图片以及连接的访问触发的访问量/点击量/统计等CRUD



本项目已经预先创建了一系列文件夹划分出下列模块:

1. app 放app,db,log的实例
2. model 文件夹负责存储数据库模型和数据库操作相关的代码
3. route 放的是路由,以及进来的请求的预处理
4. service 负责处理比较复杂的业务，把业务代码模型化可以有效提高业务代码的质量（比如用户注册，充值，下单,查询列表等等）
5. cache 负责redis以及本地缓存相关的代码
7. tools 放一些通用的小工具,小函数,方便server中各处调用
8. help 下放test(测试文件此处未补全),db_script(放历次版本的对mysql的库表结构的变更脚本),以及历次版本的说明以及一些帮助文件
9. logs 放运行产生的日志文件


## 本地运行

```shell
python runserver.py
```

项目运行后启动在3000端口（可以修改，参考Flask文档),可以配置是否启用定时任务(访问量/点击量的定时统计)

## 生产环境推荐使用nginx代理 uwsgi_config.ini
uwsgi --ini uwsgi_config.ini --daemonize /var/log/flask_crud.log
```
server {
    listen 3001 default_server;
    server_name localhost;
    location /static/ {
        root /data/;
        expires 30d;
    }
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/simpleflask.sock; # 必须和uwsgi_config.ini 中的socket配置一致
        # 并且需要权限
    }
}
```