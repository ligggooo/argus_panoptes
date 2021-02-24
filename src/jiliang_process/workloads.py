from jiliang_process.process_monitor import task_monitor
from threading import Thread
import time


@task_monitor.normal_task_deco
def A():
    raise Exception("test exception")
    return "A"


@task_monitor.normal_task_deco
def B(a):
    res = a+"B"
    for i in range(10):
        d = D(i)
        res += d
    return res


@task_monitor.normal_task_deco
def C(b):
    tl = []
    for i in range(10):
        t= Thread(target=E,args=("e",))
        tl.append(t)
    [t.start() for t in tl]
    [t.join() for t in tl]
    return b+"C"


@task_monitor.cross_thread_deco("E")
def E(c):
    time.sleep(1)
    print(c)

@task_monitor.normal_task_deco
# @task_monitor.loop_task_deco
def D(x):
    return "D%d"%x

@task_monitor.cross_process_deco("test_cross_process")
def xp_test(parent_id,batch_id):
    try:
        A()
    except Exception as e:
        print(e)
    B("xp_test")