#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : my_dispatch.py
# @Time      : 2021/3/22 21:47
# @Author    : Lee
import sys


def mydispatch(frame, event, arg):
    print("lee_debug", frame, event, arg)
    print("lee_debug2", frame.f_code.co_name)
    if frame.f_code.co_name == "hello":
        print("======", frame.f_code.co_name, frame.f_code, "======")

def trace_dispatch(frame, event, arg):
    # print("lee_debug", frame, event, arg)
    # print("----> ", frame.f_code.co_name)
    if event == "c_call":
        c_func_name = arg.__name__
    elif event == "call" and frame.f_code.co_name in["hello", "hehe"]:

        print(frame.f_locals)
        frame.f_locals.update({"xx":1213})

if __name__ == "__main__":
    pass