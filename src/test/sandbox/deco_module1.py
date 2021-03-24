#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : deco_module1.py
# @Time      : 2021/3/24 10:39
# @Author    : Lee

import  importlib

def deco1(func):
    def wrapper(*args,**kwargs):
        print(func.__name__,"被deco1包装过的函数")
        res = func(*args,**kwargs)
        return res
    return wrapper

def deco2(func):
    def wrapper(*args,**kwargs):
        print(func.__name__,"被deco2包装过的函数")
        res = func(*args,**kwargs)
        return res
    return wrapper



def chain_get(mobj, chain):
    for c in chain:
        mobj = getattr(mobj, c)
    return mobj

def chain_import(import_chain):
    tokens = import_chain.strip().split(".")
    if len(tokens) == 0:
        return importlib.__import__(import_chain)
    root = tokens[0]
    rest = tokens[1:]
    deco_root_module = importlib.import_module(root)
    ret = chain_get(deco_root_module, rest)
    return ret


def deco_module(module, deco_rules):
    print(module, deco_rules)
    for deco_rule in deco_rules:
        print("--替换", deco_rule)
        to_deco_name, deco_name = deco_rule
        deco = chain_import(deco_name)
        tokens = to_deco_name.strip().split(".")
        target = chain_get(module, tokens)
        parent = chain_get(module, tokens[:-1])
        end = tokens[-1]
        setattr(parent,end,deco(target))


if __name__ == "__main__":
    import mypack
    deco_module(mypack, ("hehe", "deco_module1.deco1"))
    deco_module(mypack, ("hello", "deco_module1.deco1"))
    mypack.hehe(1)
    mypack.hello(1)
