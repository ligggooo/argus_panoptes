#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : pdb_t.py
# @Time      : 2021/3/22 21:08
# @Author    : Lee


from dcs_task import road_public_func
print(dcs_task.road_public_func)

dcs_task.road_public_func
import jiliang_process.process_monitor as pm
from celery import  Celery
import pdb
import sys, os
from my_dispatch import mydispatch, trace_dispatch
# sys.setprofile(trace_dispatch)
# import mypack
from jiliang_process.boot.mypack import hello,hehe
from mypack import hello as hello2

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




from mypack import main2
import matplotlib.colorbar

if __name__ == '__main__':
    # sys.modules[__name__].hello.hello = sys.modules[__name__].hello.hehe
    print(sys.argv, "in script")
    main2()


