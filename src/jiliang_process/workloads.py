from jiliang_process.process_monitor import task_monitor
from threading import Thread
import time
import random

@task_monitor.normal_task_deco
def normal_task_throws_exception():
    time.sleep(1)
    dice = random.random()
    if dice >0.5:
        raise Exception("test exception")
    else:
        pass
    return "A"


@task_monitor.normal_task_deco
def normal_task_with_a_loop(a):
    res = a+"B"
    for i in range(3):
        d = normal_task_sleeps(i)
        res += d
    return res


@task_monitor.normal_task_deco
def normal_task_starts_multiple_threads(b):
    tl = []
    for i in range(3):
        t= Thread(target=thread_func, args=("e",))
        tl.append(t)
    [t.start() for t in tl]
    [t.join() for t in tl]
    return b+"C"


@task_monitor.cross_thread_deco("E")
def thread_func(c):
    dice = random.random()
    if dice > 0.6:
        raise Exception("random error")
    else:
        normal_task_throws_exception()
    print(c)

@task_monitor.normal_task_deco
# @task_monitor.loop_task_deco
def normal_task_sleeps(x):
    time.sleep(2)
    return "D%d"%x

@task_monitor.cross_process_deco("test_cross_process")
def xp_test(parent_id, root_id):
    try:
        normal_task_throws_exception()
    except Exception as e:
        print(e)
    normal_task_with_a_loop("xp_test")