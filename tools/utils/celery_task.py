# -*- coding:utf-8 -*-
__author__ = "aleimu"
__date__ = "2018-09-29"
__doc__ = """使用celery和redis做异步服务,如向手机发送短信提醒,发邮件等"""

import celery
import traceback
from tools.utils.logger import logger


celery = celery.Celery()
celery.config_from_object('cache/celery_config')
# celery define
sms_queue = 'sub_push'
sms_template = 'push_srv.common_use'  # 使用短信通用模板,短信全部内容由自己定
SMS_FLAG = True

# 发送短信
def send_celery(telephones, msg, celery_route=sms_template, queue=sms_queue):
    if not SMS_FLAG:
        return False
    logger.info('start send sms,telephone:%s,msg:%s' % (telephones, msg))
    try:
        if not telephones:
            logger.info('telephones is null')
            return False
        if not isinstance(telephones, list):
            telephones = [telephones]
        for telephone in telephones:
            result = celery.send_task(celery_route, args=[telephone, msg], queue=queue)
            if not result:
                return False
            logger.info(
                'send_sms celery_rout:%s,telephone:%s,msg:%s，result：%s ' % (celery_route, telephone, msg, result))
        return True
    except:
        logger.error('send_sms error:%s,telephones:%s' % (traceback.format_exc(), telephones))

# telephone = "XXXX"
# dowm_msg = " 您账号已被平台注销使用，特此通知"
# send_celery(telephone, dowm_msg)
