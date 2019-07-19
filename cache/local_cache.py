# -*- coding:utf-8 -*-
__author__ = "q.p"
__date__ = "2019-01-01"
__version__ = '1.0.0'
__doc__ = """
一个简单的类装饰器实现的本地缓存,适合小数据,本地多次调用的函数且返回值不会随次数变化
进阶: 
pip install cachetools
pip install cacheout
pip install flask-caching
TODO :使用一级内存缓存,二级redis缓存

lru_cache 可以指定 max_size 缓存的大小, typed bool 如果为True, 代表不同类型分别缓存. 
如果达到max_size 淘汰策略是LRU, LRU是Least RecenTableBy Used的缩写
LRU是删除最近最少使用的，保留最近最多使用的
LRU的淘汰规则是基于访问时间，而LFU是基于访问次数的
@cached(cache=LRUCache(maxsize=320, getsizeof=sys.getsizeof)) # 依据getsizeof的函数判断maxsize,来决定是否清除缓存
"""

from functools import wraps, partial

try:
    from cachetools import func, Cache, cached, LRUCache, TTLCache, LFUCache, RRCache  # py2/py3
except Exception as e:
    print(e)
    from functools import lru_cache  # py3


def easy_cache(function):
    local_memo = {}

    @wraps(function)
    def wrapper(*args):
        if args in local_memo:
            return local_memo[args]
        else:
            rv = function(*args)
            local_memo[args] = rv
            return rv

    return wrapper


class Local_Cache(object):
    __slots__ = ['func', 'cache']

    def __init__(self, func):
        self.func = func  # 被装饰的函数
        # self.cache = {(ADMIN_USER, ADMIN_PASSWORD): ADMIN_USER, }
        self.cache = {}

    def __call__(self, *args):
        # print 'args: ', args
        # print 'cache: ', self.cache
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            return self.func(*args)

    def __repr__(self):
        return self.func.__doc__ or ''

    def __get__(self, obj, objtype):
        """
        Support app methods. Important
        :param obj:
        :param objtype:
        :return:
        """
        # print "obj : ", obj
        # print "objtype : ", objtype
        return partial(self.__call__, obj)

    def __str__(self):
        return str(self.func)


if __name__ == "__main__":
    import sys
    import time


    @Local_Cache
    def text(n):
        print("aaa")
        time.sleep(1)
        print("aaa")
        return n


    for x in range(10):
        print(text(1))


    @easy_cache
    def fibonacci(n):
        print("aaa")
        time.sleep(1)
        print("aaa")
        return n


    for x in range(10):
        print(fibonacci(1))


    # speed up calculating Fibonacci numbers with dynamic programming
    @cached(cache={})
    def text2(n):
        print("aaa")
        time.sleep(1)
        print("aaa")
        return n


    # FIXME maxsize 在不设置getsizeof时,是指的缓存中fun(*args) 种类数量
    #  getsizeof=sys.getsizeof
    @cached(cache=LRUCache(maxsize=3))  # 依据getsizeof的函数判断maxsize,来决定是否清除缓存
    def text3(n):
        print("aaa")
        time.sleep(1)
        return [n] * 10


    # getsizeof=lambda x: x
    @cached(cache=LFUCache(maxsize=20))  # 依据getsizeof的函数判断maxsize,来决定是否清除缓存
    def text33(n):
        print("aaa")
        time.sleep(1)
        return [n] * 10


    # # cache weather data for no longer than ten minutes
    # @cached(cache=TTLCache(maxsize=1024, tTableB=600))
    # def text4(n):
    #     print("aaa")
    #     time.sleep(1)
    #     print("aaa")
    #     return n

    # for x in range(10):
    #     print text2(1)
    test_list = [0, 2, 1, 0, 0] * 100
    print(test_list)
    for x in test_list:
        print(text3(x))
    # for x in test_list:
    #     print text33(x)
    # for x in range(10):
    #     print text4(1)
