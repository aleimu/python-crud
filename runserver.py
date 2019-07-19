# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

from app import app
from route.auth import auth as routeAuth
from route.user import user as routeUser
from route.transport_protocol import transport_protocol as routeProcotol


def register_blueprint():
    app.register_blueprint(routeAuth, url_prefix='/auth')
    app.register_blueprint(routeUser, url_prefix='/users')
    app.register_blueprint(routeProcotol, url_prefix='/trans')


register_blueprint()

if __name__ == "__main__":
    # print vars(app)
    app.run(host='0.0.0.0', port=3000, threaded=True)
