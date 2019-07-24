# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

from app import app
from route import auth, advert


def register_blueprint():
    app.register_blueprint(auth)
    app.register_blueprint(advert)


register_blueprint()

if __name__ == "__main__":
    # print(vars(app))
    from app import scheduler

    app.run(host='0.0.0.0', port=3001, threaded=True)
