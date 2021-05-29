#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : test_caller.py
# @Time      : 2021/4/25 17:16
# @Author    : Lee
from test.have_fun.celery_t.tasks import add
import asyncio
from celery import group

# print(add(1, 2))
g = group(add.s(1, i) for i in range(5))
print(g)
res = g()
print(res.get())

