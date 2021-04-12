#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:Goodwillie
@file:request_test.py
@time:2021/04/10
"""
import requests

x = requests.get("http://192.168.31.110:5001/task_unique_id")
print(x.content)
if __name__ == '__main__':
    pass