#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : flase)recovery.py
# @Time      : 2021/4/27 13:01
# @Author    : Lee

import requests


try:
    requests.get("http://10.30.160.114:80/", timeout=1)
except requests.exceptions.ConnectTimeout as e:
    print(e)