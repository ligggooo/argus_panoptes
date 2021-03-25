#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : hello.py
# @Time      : 2021/3/22 21:25
# @Author    : Lee
import pdb
import subprocess
from jiliang_process.jp_exceptions import ProcessAccidentallyShutDownException, ProcessIntentionallyShutDownException
from jiliang_process.process_monitor import task_monitor

def yes(xxx):
    print(xxx)


def hello(n=None):
    import __main__
    print(__main__)
    # pdb.set_trace()
    print("hello world!", n)
    yes("yes world")


def hehe(n=None):
    # pdb.set_trace()
    print("hehe world!", n)
    print(locals())
    yes("no world")


class X:
    a = 2


def main2():
    # profile.run("hello()")
    hello(2131231)
    hehe(123123213)
    msg="{}"
    msg = task_monitor.pack_monitor_params_into_str(msg)
    res_semantic_dist = subprocess.Popen(
        ['python', "sub_task.py",msg],
        shell=False,
        stdin=None,
        stderr=None,
        stdout=None,
        cwd=".")
    ret_code = res_semantic_dist.wait()
    print(ret_code)
    if ret_code == 0:
        raise ProcessIntentionallyShutDownException(ret_code==0, "ret_code==0")
    else:
        raise ProcessAccidentallyShutDownException("ret_code!=0", "ret_code!=0")


if __name__ == "__main__":
    hello()
    cmd = """
print(1231)
exit(-1)
    """
    exit(-1)
    exec(cmd)
    print("end")
