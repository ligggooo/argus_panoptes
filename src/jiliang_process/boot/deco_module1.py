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
        try:
            mobj = getattr(mobj, c)
        except AttributeError as e:
            print("--路径配置错误", e)
            return None
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


def deco_module(module,module_name,deco_rules):
    print(module, module_name, deco_rules)
    if module_name != module.__name__:
        """
        import dist_road_topo.dist_road_network as dist_road
        module_name 是  dist_road_topo.dist_road_network，
        结果__import__传进来的是dist_road_topo，所以还得先get到dist_road_network
        """
        module_name_tokens = module_name.split(".")
        module = chain_get(module, module_name_tokens[1:])
        if not module:
            raise Exception("导包错误，规则不明")
    status = True
    for deco_rule in deco_rules:
        print("--装饰", deco_rule)
        to_deco_name, deco_name = deco_rule
        deco = chain_import(deco_name)
        tokens = to_deco_name.strip().split(".")
        parent = chain_get(module, tokens[:-1])
        if not parent:
            status = False
            continue
        target = chain_get(module, tokens)
        if not getattr(target,"_lee_decorated",None):
            end = tokens[-1]
            setattr(parent,end,deco(target))
            getattr(parent,end)._lee_decorated = True
        else:
            print("--装饰已经应用过", deco_rule)
    return status

from jiliang_process.process_monitor import task_monitor

demo_deco_normal = task_monitor.normal_task_deco(show_position_arg=0)

if __name__ == "__main__":
    import mypack
    deco_module(mypack, ("hehe", "deco_module1.deco1"))
    deco_module(mypack, ("hello", "deco_module1.deco1"))
    mypack.hehe(1)
    mypack.hello(1)
