#!/usr/bin/python
# -*- coding:utf-8 -*-
__doc__ = "如果有功能用到大量使用requests的场景,可以参考此文件中的方法写,但不建议直接用"

import requests
import traceback

S = requests.Session()


def api_requests(method, url, params, headers, is_param=True, times=1):
    """
    调用其他后端接口,需要数据返回格式统一
    :param method: 请求方法
    :param url: 请求地址 base_url + url
    :param params: 请求参数
    :param times: 超时时间
    :param is_param: 传参方式
    :param headers:
    :return:
    """
    method = method.upper()
    timeout = 10
    print('request url: {}, request params: {}'.format(url, params))
    for i in range(times):
        try:
            if method == 'POST':
                resq = S.post(url, json=params, headers=headers, timeout=timeout)
            elif method == 'GET':
                resq = S.get(url, params=params, headers=headers, timeout=timeout)
            elif method == 'PUT':
                if is_param:
                    resq = S.put(url, params=params, headers=headers, timeout=timeout)
                else:
                    resq = S.put(url, json=params, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                resq = S.delete(url, headers=headers, timeout=timeout)
            elif method == 'PATCH':
                resq = S.patch(url, data=params, headers=headers, timeout=timeout)
            else:
                return None, 'request method error'
            print('request url: {}, resq: {}'.format(url, resq))
            if resq.status_code == 200:
                try:
                    res_json = resq.json()
                    return res_json
                except Exception:
                    # traceback.print_exc()
                    return resq.content
            else:
                continue
        except:
            if i + 1 == times:
                traceback.print_exc()
                return None
            else:
                continue


def requests_wx(method, url, **kwargs):
    TIMEOUT = 3
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
        result = True if res_json.get('errcode', 0) == 0 else False
        return result, res_json
    except Exception:
        # traceback.print_exc()
        return True, res.content
