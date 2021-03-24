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
    print("----> ", frame, event, arg, frame.f_code.co_name)
    try:
        print(":: ", frame.f_locals)
    except Exception as e:
        print(e, "未知原因")
    if event == "c_call":
        c_func_name = arg.__name__
        # print("----> ", frame.f_code.co_name,c_func_name)
    elif event == "call" and frame.f_code.co_name == "_find_and_load":
        print("in", frame.f_locals)
    elif event == "call" and frame.f_code.co_name in["hello", "hehe","_find_and_load"]:
        print("lee_debug", frame, event, arg)
        # print("----> ", frame.f_code.co_name)
        print("in",frame.f_locals)
        if(frame.f_locals.get("name") == "mypack"):
            frame.f_locals.update({"xx":1213,"n":"what??","name":"fake"})
    elif event == "return" and frame.f_code.co_name in["hello", "hehe","_find_and_load"]:
        print("lee_debug", frame, event, arg)
        # print("----> ", frame.f_code.co_name)
        print(frame.f_locals)
        frame.f_locals.update({"n":"what??"})
        print(frame.f_locals)


if __name__ == "__main__":
    pass