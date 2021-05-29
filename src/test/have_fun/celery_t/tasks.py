#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : tasks.py
# @Time      : 2021/4/15 17:26
# @Author    : Lee
import os
import time
from test.have_fun.celery_t.celery_app import app
import sys

@app.task
def add(a, b):
    if b==3:
        raise RuntimeWarning("b==3")
    sys.stdout.write("===>>")
    for i in range(5):
        msg = str(i)+"=>"
        sys.stdout.write(msg)
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n")
    return a+b