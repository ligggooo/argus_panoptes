
import threading

import time
import unittest
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed

import numpy as np
from jiliang_process.jlp_release_package.process_monitor import EmptyProcessMonitor
from jiliang_process.process_monitor import task_monitor
# task_monitor = EmptyProcessMonitor()
from test.unitest.utils import holder, speed_deco, timer_deco, holder2, concurrent_tester
from monitor_server.settings.conf import config

TASK_RECORDER_URL= config.TASK_RECORDER_URL
TASK_UNIQUE_ID_URL= config.TASK_UNIQUE_ID_URL
task_monitor.re_config(TASK_RECORDER_URL=TASK_RECORDER_URL,
                       TASK_UNIQUE_ID_URL=TASK_UNIQUE_ID_URL)



@task_monitor.normal_task_deco()
def in_fast_job():
    time.sleep(0.1)
    raise Exception("故意失败的")


def fast_job():
    start = time.time()
    try:
        in_fast_job()
    except Exception as e:
        print(e)
    delta = time.time()-start
    holder.append(delta)


def slow_job():
    time.sleep(1)


@speed_deco
def part1():
    pool = ThreadPoolExecutor(max_workers=100)
    res = [pool.submit(fast_job) for i in range(10000)]
    for future in as_completed(res):
        print(future.result())


@task_monitor.normal_task_deco()
@speed_deco
def part2(concurreny=130, job_size=50000):
    concurrent_tester(fast_job,concurreny, job_size)


@timer_deco
def get_id():
    import requests,json
    r = requests.get(TASK_UNIQUE_ID_URL)
    print(r.content)
    dd = json.loads((r.content.decode("utf-8")))
    holder2.append(dd.get("task_unique_id"))


@timer_deco
@task_monitor.normal_task_deco()
def empty_task(interval):
    time.sleep(interval)
    return None


class MyTestCase(unittest.TestCase):
    @task_monitor.root_deco("压测根节点")
    @speed_deco
    def test_something(self):
        part1()

    @task_monitor.root_deco("压测2根节点 大并发数 大任务 计时")
    @speed_deco
    def test_something_else(self):
        part2(concurreny=30, job_size=50000)

    def test_unique_id(self):
        concurrent_tester(get_id,100,2000)
        print("=====average resp time %f ==========", np.mean(holder[-40:-1]), len(holder2), len(set(holder2)))

    @task_monitor.root_deco("压测3根节点 无并发 无限任务 计时")
    def test_resp(self):
        concurrent_tester(empty_task, 30, 20000, args=[0,])
        print("=====average resp time %.5f %d %d==========" % (np.mean(holder), len(holder2), len(set(holder2))))
        with open("./reports/concurrent_test_002", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)


if __name__ == '__main__':
    unittest.main()
