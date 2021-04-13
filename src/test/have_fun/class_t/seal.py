#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : seal.py
# @Time      : 2021/3/19 8:52
# @Author    : Lee


class ZZ:
    def _zzz(self):
        print(12321)

    def __zzz(self):
        print(12321)

print("i am imported")

__x = 2
_y = 2
z=2
if __name__ == "__main__":
    z=ZZ()
    z._zzz()
    z.__zzz()