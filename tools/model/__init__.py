# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'

from tools.utils.database import InitDB

# 通用定义
OK = 1000
SERVER_ERR = 2000
NO_DATA = 3000
DB_ERROR = 4000

from .user import User, User2
from .ad_style import AdStyle, AdStyle2
from .ad_ctr import AdCtr, AdCtr2
from .ad_group import AdGroup, AdGroup2
from .ad_image import AdImage, AdImage2

__all__ = ['AdStyle', 'AdCtr', 'AdGroup', 'AdImage', 'User', 'AdStyle2', 'AdCtr2', 'AdGroup2', 'AdImage2', 'User2', ]
