#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   vm_001.py
@Time    :   2021/04/15 21:57:13
@Author  :   Lee 
@Version :   1.0
@Contact :   null@null.com
@License :   None
@Desc    :   None
'''

# here put the import lib


import sys

x = sys.modules["builtins"].exec
y = sys.modules["builtins"].compile


def my_exec(*args,**kwargs):
    print("my_exec", args,kwargs)
    x(*args, **kwargs)

def my_compile(*args,**kwargs):
    print("my_compile", args,kwargs)
    c = y(*args, **kwargs)
    return c

sys.modules["builtins"].exec = my_exec
sys.modules["builtins"].compile = my_compile


# exec(open(sys.argv[1]).read())
file = sys.argv[1]
code = open(file).read()
c = compile(code,file,"exec")
# exec(c)
for i in range(60000):
    print(chr(i))

