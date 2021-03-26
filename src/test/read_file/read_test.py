#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : read_test.py
# @Time      : 2021/3/25 17:41
# @Author    : Lee


if __name__ == "__main__":
    import os
    p =os.path.realpath(__file__)
    print(p)
    f=open(p)
    while 1:
        z = f.read(13)
        print(z,end='')
        if len(z)==0:
            break