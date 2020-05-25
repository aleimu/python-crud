# coding: utf-8
__doc__ = "微信支付和退款API相关接口 https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=9_1#"

import os
import hashlib
import time
import traceback
import random
import requests
import platform
import xmltodict
from bs4 import BeautifulSoup

try:
    from lxml import etree
except ImportError:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree
# 微信配置基础数据
WPC = {
    'APPID': '小程序id',  # 小程序id
    'APPSECRET': '小程序密钥',  # 小程序密钥
    'MCHID': '商户号',  # 商户号
    'KEY': '商户密钥',  # 商户密钥
    'GOODDESC': '支付名称',  # 支付名称
    'NOTIFY_URL': '回调地址',  # 回调地址
    'REFUND_NOTIFY_URL': '退款回调地址',  # 退款回调地址
}
cert_file_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "cert")
key_path = os.path.join(cert_file_path, "apiclient_key.pem")
cert_path = os.path.join(cert_file_path, "apiclient_cert.pem")
deploy = platform.system()
if deploy == "Windows":
    print("OS is Windows!!!")
    cert = (key_path, cert_path)
else:
    print("OS is Linux!!!")
    cert = (cert_path, key_path)

pay_headers = {'Content-Type': 'application/xml'}
trade_state = {'SUCCESS': '支付成功', 'REFUND': '转入退款', 'NOTPAY': '未支付', 'CLOSED': '已关闭', 'REVOKED': '已撤销',
               'USERPAYING': '用户支付中', 'PAYERROR': '支付失败'}


def getNoncestr(length=32):
    """产生随机字符串，不长于32位"""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    strs = []
    for x in range(length):
        strs.append(chars[random.randrange(0, len(chars))])
    return "".join(strs)


def get_sign(data_dict, key):  # 签名函数，参数为签名的数据和密钥
    params_list = sorted(data_dict.items(), key=lambda e: e[0], reverse=False)  # 参数字典倒排序为列表
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list) + '&key=' + key
    # 组织参数字符串并在末尾添加商户交易密钥
    md5 = hashlib.md5()  # 使用MD5加密模式
    md5.update(params_str.encode())  # 将参数字符串传入
    sign = md5.hexdigest().upper()  # 完成加密并转为大写
    return sign


def trans_dict_to_xml(dict_data):
    xml = ['<xml>']
    for k, v in dict_data.items():
        xml.append('<{0}>{1}</{0}>'.format(k, v))
    xml.append('</xml>')
    return ''.join(xml)


# def trans_dict_to_xml(data_dict):  # 定义字典转XML的函数
#     data_xml = []
#     for k in sorted(data_dict.keys()):  # 遍历字典排序后的key
#         v = data_dict.get(k)  # 取出字典中key对应的value
#         if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
#             v = '<![CDATA[{}]]>'.format(v)
#         data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
#     return '<xml>{}</xml>'.format(''.join(data_xml))  # 返回XML

def trans_xml_to_dict(xml_data):
    try:
        soup = BeautifulSoup(xml_data, features='xml')
        xml = soup.find('xml')  # 解析XML
        if not xml:
            return {}
        xml_dict = dict([(item.name, item.text) for item in xml.find_all_next()])
    except Exception:
        xml_dict = {}
        root = etree.fromstring(xml_data)
        for child in root:
            xml_dict[child.tag] = child.text
    return xml_dict


def generate_deposit_number():
    """
    生成保证金流水号
    :return:
    """
    import datetime
    number = datetime.datetime.now()
    range_str = getNoncestr(length=14).upper()
    return "D" + range_str + str(number)[0:19].replace("-", "").replace(":", "").replace(" ", "")


def prepayment_wx_order(openid, spbill_create_ip, total_fee, out_trade_no):
    """
    请求微信预下单
    """
    try:
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信统一下单地址
        prepay = {
            "appId": "",
            "nonceStr": "",
            "package": "",
            "signType": "",
            "timeStamp": "",
        }
        model = {
            "appid": WPC['APPID'],  # 小程序ID
            "body": WPC['GOODDESC'],  # 商品描述
            "nonce_str": getNoncestr(),  # 随机字符串
            "mch_id": WPC['MCHID'],  # 微信支付分配的商户号
            "notify_url": WPC['NOTIFY_URL'],  # 回调地址
            "openid": openid,  # openid
            "out_trade_no": out_trade_no,  # 商户订单号
            "spbill_create_ip": spbill_create_ip,  # 调用微信支付API的机器IP
            "total_fee": int(total_fee * 100),  # 订单总金额/ 分
            "trade_type": "JSAPI",  # 支付类型
        }
        # 签名完后加到model字典里
        model['sign'] = get_sign(model, WPC['KEY'])
        # 转换为xml格式
        xml = trans_dict_to_xml(model)
        # 然后用post请求，去获取预付单号
        response = requests.post(url, xml.encode('utf-8'), headers=pay_headers)
        # 获取下来更改格式
        msg = response.text.encode('ISO-8859-1').decode('utf-8')
        print("统一下单接口返回：{}".format(msg))
        # 把xml格式改为字典格式,需要第三方库，自行下载
        xmlresp = xmltodict.parse(msg)
        # 如果判断都正确，说明请求到了预付单号
        if xmlresp['xml']['result_code'] == 'SUCCESS':
            # 然后把数据添加到prepay字典里
            prepay['appId'] = xmlresp['xml']['appid']
            # prepay['partnerid'] = xmlresp['xml']['mch_id']
            # 生成随机字符串
            prepay['nonceStr'] = getNoncestr()
            prepay['signType'] = "MD5"
            prepay['timeStamp'] = str(int(time.time()))
            prepay['package'] = "prepay_id={}".format(xmlresp['xml']['prepay_id'])
            # 再一次排序
            prepays = get_sign(prepay, WPC['KEY'])
            # 把签名加到字典里
            prepay['sign'] = prepays
            xml = trans_dict_to_xml(prepay)
            prepay['prepayId'] = xmlresp['xml']['prepay_id']
            prepay['xml'] = xml
            prepay['code'] = '00'
            prepay['msg'] = '获取成功'
            # 返回数据
            return prepay
        else:
            prepay['code'] = '01'
            prepay['msg'] = '获取失败'
            return prepay
    except:
        traceback.print_exc()


def refund_wx_order(total_fee, out_trade_no):
    """
    请求微信退款
    """
    try:
        url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'  # 微信申请退款地址
        model = {
            "appid": WPC['APPID'],  # 小程序ID
            "nonce_str": getNoncestr(),  # 随机字符串
            "notify_url": WPC['REFUND_NOTIFY_URL'],  # 退款回调url
            "mch_id": WPC['MCHID'],  # 微信支付分配的商户号
            "out_refund_no": generate_deposit_number(),  # 商户退款单号
            "out_trade_no": out_trade_no,  # 商户订单号
            "refund_fee": int(total_fee * 100),  # 退款总金额
            "total_fee": int(total_fee * 100),  # 订单总金额
        }
        # 签名完后加到model字典里
        model['sign'] = get_sign(model, WPC['KEY'])
        # 转换为xml格式
        xml = trans_dict_to_xml(model)
        # 然后用post请求申请退款
        response = requests.post(url, xml.encode('utf-8'), headers=pay_headers, cert=cert, verify=True)
        # 获取下来更改格式
        msg = response.text.encode('ISO-8859-1').decode('utf-8')
        print("申请退款接口返回:：{}".format(msg))
        # 把xml格式改为字典格式,需要第三方库，自行下载
        try:
            data = trans_xml_to_dict(msg)
        except:
            data = xmltodict.parse(msg)['xml']
        refund = {}
        # 如果判断都正确，说明请求到了预付单号
        if data['return_code'] == 'SUCCESS':
            if data['result_code'] == 'SUCCESS' or (
                    data['result_code'] == 'FAIL' and data['err_code_des'] == '订单已全额退款'):
                refund['code'] = '00'
                refund['msg'] = '获取成功'
                # 返回数据
                return refund
            else:
                refund['code'] = '01'
                refund['msg'] = '获取失败'
                return refund
        else:
            refund['code'] = '01'
            refund['msg'] = '获取失败'
            return refund
    except:
        traceback.print_exc()


def close_wx_order(out_trade_no):
    """关闭订单
    @out_trade_no: 微信订单号
    """
    url = "https://api.mch.weixin.qq.com/pay/closeorder"
    data = {"appid": WPC['APPID'], "mch_id": WPC['MCHID'], "out_trade_no": out_trade_no, "nonce_str": getNoncestr()}
    data['sign'] = get_sign(data, WPC['KEY'])
    xml = trans_dict_to_xml(data)
    resp = requests.post(url, data=xml.encode('utf-8'), headers=pay_headers)
    print("商户关闭订单接口返回：{}".format(resp.content))
    try:
        data2 = xmltodict.parse(resp.content.decode('utf-8'))
    except Exception:
        data2 = trans_xml_to_dict(resp.content.decode('utf-8'))
    if data2.get("return_code") == "SUCCESS":
        if data2.get("return_msg") == "OK":
            return True, data2
    return False, data2


def check_wx_order(out_trade_no, action=1):
    """商户查单
    @out_trade_no: 微信订单号
    @action: 查询类型
    """
    if action == 1:  # 查询支付情况
        url = "https://api.mch.weixin.qq.com/pay/orderquery"
    elif action == 2:  # 查询退款情况
        url = 'https://api.mch.weixin.qq.com/pay/refundquery'
    else:
        return "查询参数错误!"
    data = {"appid": '自己的小程序id', "mch_id": '微信支付账户', "out_trade_no": out_trade_no,
            "nonce_str": getNoncestr()}
    data['sign'] = get_sign(data, 'GBu0OAcV5rqC4GrdFdgsYUASRgqh478h')
    xml = trans_dict_to_xml(data)
    resp = requests.post(url, data=xml.encode('utf-8'), headers=pay_headers)
    try:
        data2 = trans_xml_to_dict(resp.content.decode('utf-8'))
    except Exception:
        data2 = xmltodict.parse(resp.content.decode('utf-8')).get('xml')
    if data2.get("return_code") == "SUCCESS" and data2.get("return_msg") == "OK":
        if action == 1:  # 查询支付情况
            if data2.get("trade_state") == "SUCCESS":
                return True, data2
        elif action == 2:  # 查询退款情况
            if data2.get("return_code") == "SUCCESS":
                return True, data2
    return False, data2
