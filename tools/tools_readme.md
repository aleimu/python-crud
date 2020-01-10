#model统一管理

## 统一风格约定

    1.model的文件名为小写和下划线拼接
    2.model的class名为驼峰式
    3.model.__tablename__为数据库表名,小写和下划线拼接
    4.model的class中的行字段保持和数据库字段一致,目前有个别表不一致,未改正
    5.尽量不使用relationship和ForeignKey
    6.同一个表再多个库中都有,此表的model尽量建立在同一个文件中,区别class名
    7.model class中尽量使用kv传参,不要使用__init__位置传参,不然容易引起混乱(目前很多表都是位置传参,新表不建议这样再这样做)

## 将tools安装到系统环境,在多个项目中共用
-[X] 可以将tools作为单独模块独立出来

模块是天然的单例模式,tools中将model和常用函数打包了,可以安装到系统lib中
```shell
  python setup.py install
```

## 使用示例
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from tools.utils import db

read_dbname = "my_write_db_name"
write_dbname = "your_read_db_name"

READ_SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@host:port/%s?charset=utf8' % read_dbname
WRITE_SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@host:port/%s?charset=utf8' % write_dbname
SQLALCHEMY_TRACK_MODIFICATIONS = True

app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = READ_SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_BINDS'] = {
    'read_db': READ_SQLALCHEMY_DATABASE_URI,  # 读库
    'write_db': WRITE_SQLALCHEMY_DATABASE_URI  # 写库
}

print(vars(db))  # 查看设置前
db.set(SQLAlchemy(app), write_db=write_dbname, read_db=read_dbname)  # 配置上db引擎,具体适配每个model用到的__bind_key__=数据库名
print(vars(db))  # 对比设置后

# 导入model使用方式1
from tools.model import User

s = User.query.all()
for a in s:
    print(a.to_dict())

# 导入model使用方式2---主要在在__init__.py中添加
from tools.model import User

s = User.query.all()
for a in s:
    print(a.to_dict())


# 使用样例
@blueprint.route('/<int:app_id>', methods=['PUT'])
@require_permission('publish_app_edit')
def put(app_id):
    form, error = JsonParser(*args.values()).parse()
    if error is None:
        exists_record = App.query.filter_by(identify=form.identify).first()
        if exists_record and exists_record.id != app_id:
            return json_response(message='应用标识不能重复！')
        app = App.query.get_or_404(app_id)
        app.update(**form)
        app.save()
        return json_response(app)
    return json_response(message=error)



```