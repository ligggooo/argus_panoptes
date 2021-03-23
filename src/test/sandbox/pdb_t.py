#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : pdb_t.py
# @Time      : 2021/3/22 21:08
# @Author    : Lee

import pdb
import sys, os
from my_dispatch import mydispatch, trace_dispatch
sys.setprofile(trace_dispatch)
import profile
import hello


def main():
    p = pdb.Pdb()
    print(p)
    res = pdb.find_function("hello", "hello.py")
    print(res)
    sys.settrace(mydispatch)
    filename = "hello.py"
    mainpyfile = os.path.abspath(filename)

    hello.hello()




def main2():
    # profile.run("hello()")

    hello.hello(2131231)

if __name__ == '__main__':
    sys.modules[__name__].hello.hello = sys.modules[__name__].hello.hehe
    main2()


