import unittest
import random
from monitor_server.api.api_utils.task_id_system import g_task_unique_id
from monitor_server.api.server_views_tasks import recorder_tasks_doer,task_status_tree_cache
from settings.conf import config
from test.unitest.utils import concurrent_tester, holder, holder2, timer_deco
import numpy
# import ahttp

TASK_RECORDER_URL= config.TASK_RECORDER_URL
TASK_UNIQUE_ID_URL= config.TASK_UNIQUE_ID_URL
# task_monitor.re_config(TASK_RECORDER_URL=TASK_RECORDER_URL,
#                        TASK_UNIQUE_ID_URL=TASK_UNIQUE_ID_URL)

id = g_task_unique_id.get_id()


@timer_deco
def get_id():
    return g_task_unique_id.get_id()


@timer_deco
def get_id_through_web_backend():
    import requests, json
    r = requests.get(TASK_UNIQUE_ID_URL)
    print(r.content)
    dd = json.loads((r.content.decode("utf-8")))
    holder2.append(dd.get("task_unique_id"))



@timer_deco
def do_record_tasks_test():
    id = g_task_unique_id.get_id()
    parent_id = str(random.choice(range(636,668)))
    data = {'call_category': 0, 'sub_id': id, 'parent_id': parent_id, 'name': 'empty_task_sub', 'root_id': 634,
            'state': 0, 'desc': '', 'timestamp': 1618135988.3651254}
    recorder_tasks_doer(data)


class AccessControllerDirectly(unittest.TestCase):
    def setUp(self):
        print("重新载入缓存")
        task_status_tree_cache.clear()
        task_status_tree_cache.load()

    def test_record_tasks_with_out_web_frame_c1(self):
        concurrent_tester(do_record_tasks_test, 1, 200, args=[])
        with open("./reports/test_record_tasks_with_out_web_frame_c1", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)

    def test_record_tasks_with_out_web_frame_c10(self):
        concurrent_tester(do_record_tasks_test, 10, 2000, args=[])
        with open("./reports/test_record_tasks_with_out_web_frame_c10", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)

    def test_record_tasks_with_out_web_frame_c30(self):
        concurrent_tester(do_record_tasks_test, 30, 2000, args=[])
        with open("./reports/test_record_tasks_with_out_web_frame_c30", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)

    def test_record_tasks_with_out_web_frame_c50(self):
        concurrent_tester(do_record_tasks_test, 50, 2000, args=[])
        with open("./reports/test_record_tasks_with_out_web_frame_c50", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)


class TestUniqueId(unittest.TestCase):
    def test_task_unique_id(self):
        concurrent_tester(get_id, 20, 20000, args=[])
        print("=====average resp time %.5f  qps=%f %d %d==========" % (
        float(numpy.mean(holder)), 1/float(numpy.mean(holder)), len(holder2), len(set(holder2))))
        with open("./reports/concurrent_test_003", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)

    def test_task_unique_id_through_backend(self):
        concurrent_tester(get_id_through_web_backend, 1, 2000, args=[])
        with open("./reports/concurrent_test_003", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)



if __name__ == '__main__':
    unittest.main()
