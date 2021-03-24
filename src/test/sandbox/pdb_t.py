#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : pdb_t.py
# @Time      : 2021/3/22 21:08
# @Author    : Lee

import pdb
import sys, os
from my_dispatch import mydispatch, trace_dispatch
# sys.setprofile(trace_dispatch)
# import mypack
from mypack import hello,hehe

def traverse(tree):
    traverse_i(tree, 0)

def traverse_i(tree,i):
    if i > 6:
        return
    for tag in dir(tree):
        if tag.startswith("__") or tag.startswith("_"):
            continue
        o = getattr(tree,tag)
        print(" "*i,o)
        traverse_i(getattr(tree,tag),i+1)

# for x in sys.modules:
#     print("------%s-------" % x)
#     if x not in ["my_dispatch", "mypack"]:
#         continue
#     traverse(sys.modules.get(x))
#     print("------%s-------"%x)

def main():
    p = pdb.Pdb()
    print(p)
    res = pdb.find_function("hello", "hello.py")
    print(res)
    sys.settrace(mydispatch)
    filename = "hello.py"
    mainpyfile = os.path.abspath(filename)

    hello()




def main2():
    # profile.run("hello()")

    hello(2131231)
    hehe(123123213)

if __name__ == '__main__':
    # sys.modules[__name__].hello.hello = sys.modules[__name__].hello.hehe
    main2()


