#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : xx.py.py
# @Time      : 2021/4/10 17:23
# @Author    : Lee
import sys


original_exit = sys.modules["builtins"].exit


def my_exit(*args):
    print("this_is_my exit", args)
    original_exit(*args)


sys.modules["builtins"].exit = my_exit


class Guard:
    def __init__(self, name):
        self.name = name
        self.ok = True

    def __del__(self, ok=False):
        if not self.ok:
            print('this function has exited', ok)

    def __enter__(self):
        print('in context')

    def __exit__(self, a, b, c):
        print('get out')

# with Guard('test'):
#     exit()


def test_guard(flag):
    guard = Guard(__name__)
    if not flag:
        guard.ok = False
        exit(1)
    else:
        pass


test_guard(True)
test_guard(False)
