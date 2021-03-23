#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : hello.py
# @Time      : 2021/3/22 21:25
# @Author    : Lee
import pdb


def yes(xxx):
    print(xxx)


def hello(n=None):
    # pdb.set_trace()
    print("hello world!", n)
    yes("yes world")


def hehe(n=None):
    # pdb.set_trace()
    print("hehe world!", n)
    print(locals())
    yes("no world")


if __name__ == "__main__":
    hello()
