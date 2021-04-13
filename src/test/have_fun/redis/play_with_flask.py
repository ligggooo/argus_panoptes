#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   play_with_flask.py
@Time    :   2021/04/12 22:19:57
@Author  :   Lee 
@Version :   1.0
@Contact :   null@null.com
@License :   None
@Desc    :   None
'''

# here put the import lib


import requests,numpy,time,sys
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed



port = sys.argv[1]
w = int(sys.argv[2])
N=int(sys.argv[3])



holder = numpy.zeros([1,N])
holder2 = numpy.zeros([1,N])

def req(id):
    t = time.time()
    r = requests.get(url="http://127.0.0.1:%s/"%port)
    
    res= int(r.content)
    print(r.content,res)
    delta = time.time()-t
    holder[0,id] = delta
    return res

pool = ThreadPoolExecutor(max_workers=w)
t_v = []

for i in range(N):
    # print(f'{r.incr("xx")=}')
    h = pool.submit(req,i)
    h.id = i
    t_v.append(h)

for h in as_completed(t_v):
    print(h.result())
    holder2[0,h.id] = h.result()
    # print(delta)

print(holder)
print(holder2)
print(numpy.mean(holder), w*1/numpy.mean(holder))