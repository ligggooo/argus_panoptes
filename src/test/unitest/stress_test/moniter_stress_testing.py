import numpy
import time
import unittest
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed
import requests
from jiliang_process.process_monitor import task_monitor


task_monitor.re_config(TASK_RECORDER_URL="http://172.16.5.148:60012/record_tasks",
                  TASK_UNIQUE_ID_URL="http://172.16.5.148:60012/task_unique_id", MONITOR_DISABLED=False)

holder = []


def fast_job():
    z = requests.get("http://127.0.0.1:60010/task_unique_id")
    print(z.content)
    return z.content


@task_monitor.normal_task_deco()
def fast_job_do_nothing():
    return None


@task_monitor.normal_task_deco()
def supposed_to_be_real(c, m):
    executor = ThreadPoolExecutor(max_workers=c)
    t_v = [executor.submit(fast_job_do_nothing) for i in range(m)]
    for t in as_completed(t_v):
        print("----------------", t.result())
    print("done")


def slow_job():
    z = requests.post("http://172.16.5.148:60012/slow_job", data="this should take some time"*10)
    print(z.content)
    return z.content


def super_slow_job():
    t = time.time()
    z = requests.post("http://172.16.5.148:60012/post_test_write_db", data="this should take some time".encode("utf-8")*10)
    print(z.content)
    delta = time.time()-t
    holder.append(delta)
    return z.content


class MyTestCase(unittest.TestCase):
    def test_something(self):
        executor = ThreadPoolExecutor(max_workers=30)
        t_v = [executor.submit(fast_job) for i in range(1000)]
        for t in as_completed(t_v):
            print("get",t.result())
        print("done")

    def test_something_else(self):
        executor = ThreadPoolExecutor(max_workers=30)
        t_v = [executor.submit(slow_job) for i in range(10000)]
        cnt = 0
        for t in as_completed(t_v):
            print("post_get", t.result())
            cnt += 1
            print(numpy.mean(holder), cnt)
        print("done")
        print(numpy.mean(holder))

    def test_something_different(self):
        executor = ThreadPoolExecutor(max_workers=50)
        t_v = [executor.submit(super_slow_job) for i in range(10000)]
        cnt = 0
        for t in as_completed(t_v):
            print("post_test_write_db", t.result())
            cnt += 1
            print(numpy.mean(holder), cnt)
        print("done")
        print(numpy.mean(holder))

    @task_monitor.root_deco("性能压测")
    def test_something_real(self):
        supposed_to_be_real(c=1,m=1000)


    def test_speed_anl(self,parent_id):
        """
        SELECT avg(delta),count(delta) from
            (select a.sub_id, a.timestamp,b.timestamp,b.timestamp-a.timestamp as delta from
                (SELECT sub_id,timestamp,state from task_track where parent_id='318333' and state='0') as a
                    join
                (SELECT sub_id,timestamp,state from task_track where parent_id='318333' and state='1') as b
                    on
                a.sub_id=b.sub_id
            ) as c;
        :param parent_id:
        :return:
        """
        pass


if __name__ == '__main__':
    unittest.main()
