#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:Goodwillie
@file:generator.py
@time:2021/04/11
"""


import os,time

named_pipe = "pipetest"


os.mkfifo(named_pipe) # can not do it in windows

len_num_in_pipe = 10

def read_some(n):
    fd = os.open(named_pipe, os.O_RDONLY)
    nums = []
    for i in range(n):
        s = os.read(fd, len_num_in_pipe)
        if len(s) == 0:
            break
        else:
            num = int(s.decode("ascii"))
            nums.append(num)
    os.write(fd, b'')
    return nums


def write_some(nums):
    fd = os.open(named_pipe, os.O_RDWR)
    for n in nums:
        n_str = str(n).zfill(len_num_in_pipe).encode("ascii")
        os.write(fd,  n_str)


def get_one():
    nums = read_some(3)
    if len(nums) == 0:
        print("init --- ")
        write_some(range(1, 11))
        return 0
    elif len(nums) == 1:
        print("read 1 put back 10")
        res = nums[0]
        write_some(range(res, res+10))
        return res
    else:
        print("read 1")
        res = nums[0]
        # write_some([res+1])
        return res

if __name__ == '__main__':

    write_some(range(10))
    print(read_some(10))
    print(read_some(10))
    print(read_some(10))
    print(read_some(10))
    print(read_some(10))
    print(read_some(10))
    for i in range(20):
        print(get_one())
        time.sleep(1)
