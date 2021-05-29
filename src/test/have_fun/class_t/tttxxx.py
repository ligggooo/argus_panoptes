#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : tttxxx.py
# @Time      : 2021/4/27 10:36
# @Author    : Lee
import xxmodel as aa

class BB:
    def __del__(self):
        print("BB ....")

if __name__ == "__main__":
    bb = BB()
    print(aa)
    print(aa.__del__)