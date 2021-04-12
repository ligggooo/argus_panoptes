import unittest

from monitor_server.api.api_utils.task_id_system import g_task_unique_id
from monitor_server.api.server_views_tasks import recorder_tasks_doer
from test.unitest.utils import concurrent_tester, holder, holder2, timer_deco
import numpy

id = g_task_unique_id.get_id()


@timer_deco
def get_id():
    return g_task_unique_id.get_id()

@timer_deco
def do_record_tasks_test():
    id = g_task_unique_id.get_id()
    data = {'call_category': 0, 'sub_id': id, 'parent_id': 170924, 'name': 'empty_task_sub', 'root_id': 166254,
            'state': 0, 'desc': '', 'timestamp': 1618135988.3651254}
    recorder_tasks_doer(data)


class MyTestCase(unittest.TestCase):
    def test_task_unique_id(self):
        concurrent_tester(get_id, 20, 20000, args=[])
        print("=====average resp time %.5f %d %d==========" % (
        float(numpy.mean(holder)), len(holder2), len(set(holder2))))
        with open("./reports/concurrent_test_003", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)

    def test_record_tasks(self):
        concurrent_tester(do_record_tasks_test, 1, 2000, args=[])
        print("=====average resp time %.5f %d %d==========" % (
            float(numpy.mean(holder)), len(holder2), len(set(holder2))))
        with open("./reports/concurrent_test_005", 'w') as f:
            for delta_t in holder:
                f.write("%.5f\n" % delta_t)

if __name__ == '__main__':
    unittest.main()
