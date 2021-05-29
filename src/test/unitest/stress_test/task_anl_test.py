import time
import unittest

import numpy as np
from typing import List, Any

from monitor_server.api.api_utils.task_cache_system import KeyedDataSrc, KeyedItem, LRUCache, TaskTrackDbKeyedDataSrc, \
    TaskRecordCache


class TaskAnlTestCase(unittest.TestCase):
    def setUp(self):
        self.nums = np.random.randint(1,40, (1,1000))

    def test_something(self):
        class Record(KeyedItem):
            def __init__(self,id,val):
                super().__init__(k=id)
                self.val = val
                self.desc = time.time()

            def __repr__(self):
                return  "%s %s %s"%(self.key, self.val, self.desc)

        tc = TaskRecordCache(10)
        for i in range(20):
            tc.insert(Record(str(i), i))
            print(tc.records)

        for j in range(1000):
            r = Record(str(self.nums[0,j]), j)
            tc.insert(r)
        [print(k,len(tc.records[k])) for k in tc.records]


# ---------------------------------------------

class DataSrc(KeyedDataSrc):
    nums = np.random.randint(1, 40, (1, 1000))
    cnt = 0

    def load(self, key: str) -> KeyedItem:
        time.sleep(0.3)
        item = KeyedItem(key)
        item.val = DataSrc.nums[0, int(key)]
        return item

    def write(self, items: List[Any]):
        time.sleep(10)


class MYLRUCache(LRUCache):
    def insert(self, item: KeyedItem or None):
        super().insert(item)

    def flush(self):
        pass

    def load_all(self):
        pass


# ----------------------------------------------------

class LRUCacheTestCase(unittest.TestCase):
    def setUp(self):
        slow_data_src = DataSrc()
        cache = MYLRUCache(100, slow_data_src)

        self.slow_data_src2 = TaskTrackDbKeyedDataSrc(conn_str=None)
        self.cache2 = TaskRecordCache(20)
        self.cache = cache


    def test_main(self):
        for i in range(100):
            self.cache.get(str(i))
            print(self.cache)

    def test_main_1(self):
        for i in range(100):
            self.cache.get(str(i))
            print(self.cache)

    def test_main_2(self):
        item = self.slow_data_src2.load("305320")
        self.cache2.get("305320")
        self.cache2.load_all()
        pass


class ServerLogAnlTestCase(unittest.TestCase):

    def test_main(self):
        import re
        import matplotlib.pyplot as plt
        import numpy
        file = r"E:\workspace\tmp\monitor_server.log"
        time_list = []
        with open(file) as f:
            for line in f:
                if "[PERFORMANCE]" in line:
                    res = re.match(".*finished in ([0-9|.]*)", line)
                    try:
                        t = float(res.groups()[0])
                        if t >0.2:
                            print(line)
                        time_list.append(t)
                    except TypeError as e:
                        print(t, line)
        plt.figure()
        plt.plot(numpy.array(time_list))
        plt.show()

if __name__ == '__main__':
    unittest.main()
