"""测试用任务"""
import time

from jiliang_process.process_monitor import task_monitor,StatePoint
from jiliang_process.workloads import normal_task_throws_exception,normal_task_with_a_loop,normal_task_mult_threds,xp_test
import traceback
import multiprocessing as mp


__version__ = "语义算法v 1.0.0"
task_monitor.re_config()

@task_monitor.cross_process_deco(__version__)
def sa_celery_main(sub_task, parent_id="",root_id=None):  # 跨系统调用关联
    try:
        a = normal_task_throws_exception()
    except Exception as e:
        print(e)
        a = "error"
    b = normal_task_with_a_loop(a)
    c = normal_task_mult_threds(b)
    try:
        new_p = mp.Process(target=xp_test, kwargs={"parent_id": task_monitor.current_id,
                                          "root_id": task_monitor.root_id})
        new_p.start()
        new_p.join()
    except Exception as e:
        print(e)
        raise e
    print(c)

@task_monitor.cross_process_deco(__version__)
def main2(sub_id, parent_id="",root_id=None):  # 跨系统调用关联
    try:
        a = normal_task_throws_exception()
    except Exception as e:
        print(e)
        a = "error"
    b = normal_task_with_a_loop(a)
    c = normal_task_mult_threds(b)

    print(c)


@task_monitor.root_deco("根任务", "batch_id")
def call(batch_id): # 模拟jiliang启动一个batch之后，发起了三个子任务
    new_p_1 = mp.Process(target=sa_celery_main, kwargs={"sub_task":1,"parent_id": task_monitor.current_id,"root_id": task_monitor.root_id})
    new_p_2 = mp.Process(target=sa_celery_main,
                         kwargs={"sub_task": 2, "parent_id": task_monitor.current_id, "root_id": task_monitor.root_id})
    new_p_3 = mp.Process(target=sa_celery_main,
                         kwargs={"sub_task": 3, "parent_id": task_monitor.current_id, "root_id": task_monitor.root_id})
    pl = [new_p_1,new_p_2,new_p_3]
    [p.start() for p in pl]
    [p.join() for p in pl]


def test_main():
    import uuid
    # 假设这个就是一个批量往rabbit_mq发消息的脚本
    # 批量发了两个batch，后一个发了两次
    id1 = "batch 001"
    call(batch_id=id1)
    # id2 = "batch 002"
    # call(batch_id=id2)
    # call(batch_id=id2)



@task_monitor.normal_task_deco
def test_main_single_machine_single_thread():
    normal_task_with_a_loop("xxxx")
    normal_task_throws_exception()


@task_monitor.normal_task_deco
def test_main_single_machine_multiple_threads():
    normal_task_mult_threds("xxxx")
    normal_task_throws_exception()

# test_main_single_machine_single_thread()


# 假设这个就是一个批量往rabbit_mq发消息的脚本
if __name__ == "__main__":
    test_main()