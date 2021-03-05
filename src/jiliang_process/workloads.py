""" 测试负载 """

from threading import Thread
import time
import random
from .process_monitor import task_monitor


@task_monitor.normal_task_deco
def normal_task_throws_exception():
    """
    normal_task_throws_exception test
    :return:
    """
    time.sleep(1)
    dice = random.random()
    if dice > 0.5:
        raise Exception("test exception")
    else:
        pass
    return "A"


@task_monitor.normal_task_deco
def normal_task_with_a_loop(alpha):
    """
    normal_task_with_a_loop test
    :param alpha:
    :return:
    """
    res = alpha+"B"
    for i in range(3):
        delta = normal_task_sleeps(i)
        res += delta
    return res


@task_monitor.normal_task_deco
def normal_task_mult_threds(beta):
    """
    normal_task_starts_multiple_threads test
    :param beta:
    :return:
    """
    tsk_li = []
    for _ in range(3):
        tsk = Thread(target=thread_func, args=("e",))
        tsk_li.append(tsk)
    _ = [t.start() for t in tsk_li]
    _ = [t.join() for t in tsk_li]
    return beta+"C"


@task_monitor.cross_thread_deco("E")
def thread_func(charlie):
    """
    thread_func test
    :param charlie:
    :return:
    """
    dice = random.random()
    if dice > 0.6:
        raise Exception("random error")
    else:
        normal_task_throws_exception()
    print(charlie)


@task_monitor.normal_task_deco
# @task_monitor.loop_task_deco
def normal_task_sleeps(xenon):
    """
    normal_task_sleeps test
    :param xenon:
    :return:
    """
    time.sleep(2)
    return "D%d" % xenon


@task_monitor.cross_process_deco("test_cross_process")
def xp_test(parent_id, root_id):
    """
    xp_test
    :param parent_id:
    :param root_id:
    :return:
    """
    try:
        print(parent_id, root_id)
        normal_task_throws_exception()
    except Exception as exp:
        print(exp)
    normal_task_with_a_loop("xp_test")
