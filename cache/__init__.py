# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'
__doc__ = "缓存模块，远程使用Redis,本地使用lru_cache"

from .redis_client import *
from .keys import *
from .local_cache import *
