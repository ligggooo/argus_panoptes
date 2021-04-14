import time
import unittest

import numpy as np

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



class MYLRUCache(LRUCache):
    def insert(self, item: KeyedItem or None):
        super().insert(item)

    def flush(self):
        pass

    def load_all(self):
        pass

slow_data_src = DataSrc()
cache = MYLRUCache(100, slow_data_src)

slow_data_src2 = TaskTrackDbKeyedDataSrc()
cache2 = TaskRecordCache(20)
# ----------------------------------------------------

class LRUCacheTestCase(unittest.TestCase):
    cache = cache


    def test_main(self):
        for i in range(100):
            self.cache.get(str(i))
            print(self.cache)

    def test_main_1(self):
        for i in range(100):
            self.cache.get(str(i))
            print(self.cache)

    def test_main_2(self):
        item = slow_data_src2.load("305320")
        cache2.get("305320")
        cache2.load_all()
        pass




if __name__ == '__main__':
    unittest.main()
