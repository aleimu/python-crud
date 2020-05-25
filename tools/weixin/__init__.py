#!/usr/bin/python
# -*- coding:utf-8 -*-
__doc__ = "微信相关的函数或类,尽量保持整洁"

# 将外部依赖提前引入,微信内部从这里取
# from tools.constant import WPC, REFUND_NOTIFY_URL
# from instance.config import REDIS_URL

from .wx_pay import *
from .basic import *
