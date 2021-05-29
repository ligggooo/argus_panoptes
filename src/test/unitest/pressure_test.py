#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : pressure_test.py
# @Time      : 2021/4/9 13:49
# @Author    : Lee




import time
import requests
from functools import wraps
import numpy as np


def timer(collector):
    def timer_deco(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            t = time.time()
            res = func(*args,**kwargs)
            i_t = time.time()-t
            collector.append(i_t)
            return res
        return wrapper
    return timer_deco


c = []

@timer(c)
def get_task_unique_id():
    r = requests.get("http://172.16.5.148:60012/task_unique_id")
    # print(r.content)

def t_main():
    t = time.time()
    for i in range(1000):
        get_task_unique_id()
    print(time.time() - t)

    print(np.mean(c), np.sum(c))

import cProfile
cProfile.run("t_main()","result")


import pstats

# p = pstats.Stats(r"E:\workspace\jiliang_monitor_pr\src\monitor_server\api\api_utils\perf.log")
p=pstats.Stats("result")
p.sort_stats("time")
p.print_stats()