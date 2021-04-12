#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:Goodwillie
@file:using_redis.py
@time:2021/04/11
"""
import time

import redis

t= time.time()
r = redis.StrictRedis(host='192.168.31.110', port=6379, db=0)
print(r.set('foo', 'bar'))
print(r.get('foo'))
print(r.incr('uni_id'))
delta = time.time()-t
print(delta)
if __name__ == '__main__':
    while 1:
        t = time.time()
        # r = redis.StrictRedis(host='192.168.31.110', port=6379, db=0)
        print(r.incr('uni_id'))
        delta = time.time() - t
        print(delta)
        time.sleep(1)