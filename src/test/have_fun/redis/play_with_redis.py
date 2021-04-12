#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   play_with_redis.py
@Time    :   2021/04/12 21:56:54
@Author  :   Lee 
@Version :   1.0
@Contact :   null@null.com
@License :   None
@Desc    :   测试发现，本地单机redis生成唯一id的速度高达4600次/s
'''

# here put the import lib
import sys,time
sys.path.insert(0,".")
import redis,numpy
from monitor_server.settings.conf import RedisConn

r = redis.StrictRedis(host=RedisConn.host, 
            port=RedisConn.port,db=RedisConn.db)


print(f'{r.set("x",2)=}')
print(f'{r.get("x")=}')
print(f'{r.get("xx")=}')
print(f'{dir(r)=}')

N=10000
holder = numpy.zeros([1,N])
holder2 = numpy.zeros([1,N])

# r.hmset()
for i in range(N):
    t = time.time()
    # print(f'{r.incr("xx")=}')
    holder2[0,i] = r.incr("xx")
    delta = time.time()-t
    holder[0,i] = delta
    # print(delta)
print(holder)
print(holder2)
print(numpy.mean(holder), 1/numpy.mean(holder))


