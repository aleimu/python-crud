# -*- coding:utf-8 -*-
__author__ = "leimu"
__date__ = "2018-09-21"

from app import db


def db_session_commit():
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


class Base(object):
    __slots__ = ()

    def get_dict(self):
        dict = {}
        dict.update(self.__dict__)
        if "_sa_instance_state" in dict:
            del dict['_sa_instance_state']
        return dict

    @classmethod
    def get_first(self, **kwargs):
        obj = self.query.filter_by(**kwargs).first()
        return obj

    @classmethod
    def get_all(self, **kwargs):
        obj = self.query.filter_by(**kwargs).all()
        return obj

    def __init__(self, **kwargs):
        pass

    def save(self):
        db.session.add(self)
        db_session_commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db_session_commit()

    def add(self):
        db.session.add(self)

    def update(self, **kwargs):
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(self, k) and getattr(self, k) != v:
                required_commit = True
                setattr(self, k, v)
        if required_commit:
            db_session_commit()
        return required_commit

    @classmethod
    def upsert(self, where, **kwargs):
        """更新或新增"""
        record = self.query.filter_by(**where).first()
        if record:
            record.update(**kwargs)
        else:
            record = self(**kwargs).save()
        return record

    def to_json(self, remove=None, choose=None):
        """
        json序列化
        :param remove: 排除的字段合集
        :param choose: 选中的字段合集
        :return: dict
        """
        if not hasattr(self, '__table__'):
            raise AssertionError('<%r> does not have attribute for __table__' % self)
        elif choose:
            return {i: getattr(self, i) for i in choose}
        elif remove:
            return {i.name: getattr(self, i.name) for i in self.__table__.columns if i.name not in remove}
        else:
            return {i.name: getattr(self, i.name) for i in self.__table__.columns}


""" 使用样例
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

"""
