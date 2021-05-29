#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:Goodwillie
@file:utils.py
@time:2021/04/11
"""

from functools import wraps
import logging,time
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed
import numpy as np
import numpy

holder = []
holder2 = []
logger = logging.getLogger("stress_monitor")
logger.setLevel(logging.INFO)


def speed_deco(func):
    @wraps(func)
    def w(*args, **kwargs):
        logger.warning("%s started" % func.__name__)
        res = func(*args, **kwargs)
        logger.warning("%s finished" % func.__name__)
        return res

    return w


def timer_deco(func):
    @wraps(func)
    def w(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        delta = time.time() - start
        holder.append(delta)
        return res

    return w

def concurrent_tester(func, n, m,args=()):
    pool = ThreadPoolExecutor(max_workers=n)
    res = [pool.submit(func, *args) for i in range(m)]
    cnt = 0
    for future in as_completed(res):
        print("=============== %s %.5f %d"%(future.result(), float(np.mean(holder[-40:-1])), cnt))
        cnt += 1
    print("=====average resp time %.5f  qps=%f %d %d==========" % (
        float(numpy.mean(holder)), n*1 / float(numpy.mean(holder)), len(holder2), len(set(holder2))))