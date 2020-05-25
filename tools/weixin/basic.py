# -*- coding:utf-8 -*-
__doc__ = "微信常用API接口"

import base64
import traceback

try:
    import ujson as json
except ImportError:
    import json
import requests
import redis
from Crypto.Cipher import AES
from app.config import REDIS_URL, XCX_APP_ID, XCX_SECRET_KEY

rds = redis.from_url(REDIS_URL, decode_responses=True)
TIMEOUT = 3
try_time = 2
S = requests.Session()
access_token_err = {"errcode": 40001,
                    "errmsg": "invalid credential, access_token is invalid or not latest hints: [bfkBqfyFe-Yp9fMa!]"}


def requests_wx(method, url, **kwargs):
    try:
        res = S.request(method, url, params=kwargs.get('params'), json=kwargs.get('json'), data=kwargs.get('data'),
                        files=kwargs.get('files'), timeout=TIMEOUT)
        if res.status_code != 200:
            return False, res.content
    except Exception:
        traceback.print_exc()
        return False, None
    try:
        res_json = res.json()
        if wx_access_token_err(res_json):
            del_wx_token()
        result = True if res_json.get('errcode', 0) == 0 else False
        return result, res_json
    except Exception:
        # traceback.print_exc()
        return True, res.content


def get_wx_token(app_id=XCX_APP_ID):
    # 微信的access_token是有时效的,这里维护一份,方便每次取用
    key = WX_TOKEN.format(app_id)
    token = rds.get(key)
    if not token:
        token, expires = wx.get_access_token()
        rds.set(key, token, ex=expires - 300)
        # rds.expire(key, 3600)
    return token


def del_wx_token(app_id=XCX_APP_ID):
    key = WX_TOKEN.format(app_id)
    rds.delete(key)


def wx_access_token_err(res_json):
    """检查微信返回的错误是否和access_token时效/错误等情况有关"""
    if res_json.get("errcode") == 40001 or "access_token" in res_json.get("errmsg", ""):
        return True
    else:
        return False


class WeiXinBasic():
    """
    微信相关基础模块
    """

    def __init__(self, app_id, app_secret, access_token=None):
        """
        初始化
        :param app_id:　app_id
        :param app_secret: app_secret
        """
        self._app_id = app_id
        self._app_secret = app_secret
        self._access_token = access_token
        self._base_url = 'https://api.weixin.qq.com/'  # 微信接口主域名
        self._base_url_back = 'https://api2.weixin.qq.com/'  # 微信接口备灾主域名
        self._base_param = {
            'appid': self._app_id,
            'secret': self._app_secret
        }
        self.S = requests.Session()

    def decrypt(self, encrypted_data, iv, session_key):
        """
        解密
        :param encrypted_data:　微信返回的加密数据
        :param iv: 　加密算法的初始向量
        :return:　解密后信息decrypted
        decrypted = {
            "phoneNumber": "13580006666",
            "purePhoneNumber": "13580006666",
            "countryCode": "86",
            "watermark":
                {
                    "appid":"APPID",
                    "timestamp": TIMESTAMP
                }
        }
        """
        # base64 decode
        session_key = base64.b64decode(session_key)
        encrypted_data = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv)
        cipher = AES.new(session_key, AES.MODE_CBC, iv)
        user_data = self._unpad(cipher.decrypt(encrypted_data))
        decrypted = json.loads(user_data)
        if decrypted['watermark']['appid'] != self._app_id:
            print("wx_user_data:", user_data)
            raise Exception('Invalid Buffer')
        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

    def req_weixin(self, url, method, params_data, success_code=[0], try_time=5, time_out=2):
        """
        调用微信接口
        :param url_key:
        :param params_data:
        :param success_code:
        :param try_time:
        :param time_out:
        :return:
        """
        method = method.upper()
        rs = False, None
        url = '{}{}'.format(self._base_url, url)

        # todo 备灾域名使用
        for i in range(try_time):
            try:
                if method == 'POST':
                    resq = self.S.post(url, data=params_data, timeout=time_out)
                elif method == 'GET':
                    resq = self.S.get(url, params=params_data, timeout=time_out)
                else:
                    rs = False, 'method is error'
                    break

                reback = resq.json()
                req_status = int(reback.get('errcode')) if reback.get('errcode') else None
                if req_status and success_code and req_status not in success_code:
                    rs = False, reback
                    continue
                else:
                    rs = True, reback
                break
            except Exception as e:
                rs = False, e
        return rs

    def get_access_token(self):
        """ 获取授权凭证（access_token） """
        api = 'https://api.weixin.qq.com/cgi-bin/token'
        params = {
            'appid': self._app_id,
            'secret': self._app_secret,
            'grant_type': 'client_credential',
        }
        err, res = requests_wx("GET", api, params=params)
        self._access_token = res.get('access_token') if err else None
        expires_in = res.get('expires_in') if err else 3600
        print("***", self._access_token, expires_in, res)
        return self._access_token, expires_in

    def code_to_session(self, js_code):
        """获取用户会话秘钥 session_key/unionid/openid,其中unionid为"""
        url = 'sns/jscode2session'
        params = {
            'js_code': js_code,
            'grant_type': 'authorization_code'
        }
        params.update(self._base_param)
        # 40029 js_code无效,返回给业务系统进行处理
        err, res = self.req_weixin(url, 'GET', params, success_code=[0])
        return err, res

    def access_token_code(self, app_id, secret, code):
        """ 通过code换取网页授权access_token """
        api = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': self._app_id,
            'secret': self._app_secret,
            'code': code,
            'grant_type': 'authorization_code',
        }
        return requests_wx("GET", api, params=params)

    # --------------------------------------------------------------------------- #
    # 小程序全局唯一后台接口调用凭据（access_token）。调用绝大多数后台接口时都需使用 access_token
    # https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/access-token/auth.getAccessToken.html
    # --------------------------------------------------------------------------- #

    def check_token(self, access_token, openid):
        """ 检验授权凭证（access_token）是否有效 """
        api = 'https://api.weixin.qq.com/sns/auth'
        params = {
            'access_token': access_token,
            'openid': openid,
        }
        return requests_wx("GET", api, params=params)

    def refresh_token(self, refresh_token):
        """ 刷新access_token """
        api = 'https://api.weixin.qq.com/sns/oauth2/refresh_token'
        params = {
            'appid': self._app_id,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        return requests_wx("GET", api, params=params)

    def jscode2session(self, js_code):
        """ 临时登录凭证校验接口 """
        api = 'https://api.weixin.qq.com/sns/jscode2session'
        params = {
            'appid': self._app_id,
            'secret': self._app_secret,
            'js_code': js_code,
            'grant_type': 'authorization_code',
        }
        return requests_wx("GET", api, params=params)

    def userinfo(self, access_token, openid):
        """ 拉取用户信息 """
        api = 'https://api.weixin.qq.com/sns/userinfo'
        params = {
            'access_token': access_token,
            'openid': openid,
        }

        return requests_wx("GET", api, params=params)

    def custom_send(self, access_token, data, **kwargs):
        """ 发送客服消息 """
        api = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={}'.format(access_token)
        data.update(**kwargs)
        return requests_wx("POST", api, json=data)

    def short_url(self, access_token, url):
        """生成短连接"""
        data = {"action": "long2short", "long_url": url}
        api = 'https://api.weixin.qq.com/cgi-bin/shorturl?access_token={}'.format(access_token)
        return requests_wx("POST", api, json=data)

    # --------------------------------------------------------------------------- #
    # 微信ocr
    # https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/ocr/ocr.bankcard.html
    # --------------------------------------------------------------------------- #

    def wx_ocr(self, access_token, img_type, img_url):
        data = {"type": "photo", "img_url": img_url, "access_token": access_token}
        if img_type == "bankcard":  # 银行卡
            data = {"img_url": img_url, "access_token": access_token}
            api = "https://api.weixin.qq.com/cv/ocr/bankcard?access_token={}".format(access_token)
        elif img_type == "drivinglicense":  # 驾驶证
            api = "https://api.weixin.qq.com/cv/ocr/drivinglicense?access_token={}".format(access_token)
        elif img_type == "idcard":  # 身份证
            api = "https://api.weixin.qq.com/cv/ocr/idcard?access_token={}".format(access_token)
        elif img_type == "driving":  # 行驶证
            api = "https://api.weixin.qq.com/cv/ocr/driving?access_token={}".format(access_token)
        elif img_type == "bizlicense":  # 营业执照
            api = "https://api.weixin.qq.com/cv/ocr/bizlicense?access_token={}".format(access_token)
        else:
            return None
        return requests_wx("POST", api, params=data)

    # --------------------------------------------------------------------------- #
    # 小程序二维码
    # https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/qr-code/wxacode.createQRCode.html
    # --------------------------------------------------------------------------- #

    def getwxacode(self, access_token, path, **kwargs):
        """ 接口A: 适用于需要的码数量较少的业务场景 """
        api = 'https://api.weixin.qq.com/wxa/getwxacode?access_token={}'.format(access_token)
        data = {'path': path}
        data.update(**kwargs)
        return requests_wx("POST", api, json=data)

    def getwxacodeunlimit(self, access_token, scene, **kwargs):
        """ 接口B：适用于需要的码数量极多的业务场景 """
        api = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}'.format(access_token)
        data = {'scene': scene, "auto_color": True}
        data.update(**kwargs)
        return requests_wx("POST", api, json=data)

    def createwxaqrcode(self, access_token, path, **kwargs):
        """ 接口C：适用于需要的码数量较少的业务场景 """
        api = 'https://api.weixin.qq.com/cgi-bin/wxaapp/createwxaqrcode?access_token={}'.format(access_token)
        data = {'path': path}
        data.update(**kwargs)
        return requests_wx("POST", api, json=data)

    # --------------------------------------------------------------------------- #
    # 发送订阅消息
    # https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/subscribe-message/subscribeMessage.send.html
    # --------------------------------------------------------------------------- #
    def send_msg(self, access_token, touser, template_id, msg):
        """ 发送订阅消息 """
        api = 'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={}'.format(access_token)
        data = {'touser': touser, "template_id": template_id, "data": msg}
        return requests_wx("POST", api, json=data)


wx = WeiXinBasic(XCX_APP_ID, XCX_SECRET_KEY)
