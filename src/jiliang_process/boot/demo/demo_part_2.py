#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : demo_part_2.py
# @Time      : 2021/5/11 14:25
# @Author    : Lee

import sys

def hello(s):
    print("hello %s"%s)


def goodbye(s):
    print("goodbye %s"%s)


def main():
    print("demo main start")
    hello(sys.argv)
    goodbye(sys.argv)
    print("demo main ends")