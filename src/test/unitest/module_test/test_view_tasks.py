import json
import unittest

import requests

from settings.conf import config


class TasksTestCase(unittest.TestCase):
    def check(self, dict_obj, key_word):
        print(dict_obj)
        self.assertIn("data", dict_obj, "无数据体")
        self.assertIn("code", dict_obj, "无返回状态码")
        code = dict_obj['code']
        self.assertEqual(code, 200, "请求失败")
        self.assertIn("code", dict_obj, "无数据体")
        data = dict_obj['data']
        cnt = data['count']
        data_vector = data['data']
        self.assertTrue(len(data_vector) <= cnt, "数据子列表长度应该小于总长度")
        for p in data_vector:
            tag = p['tag']
            root_id = p["root_id"]
            print(tag, root_id)
            self.assertTrue((key_word in tag) or (key_word == root_id))

    def test_task_search(self):
        url = "%s/%s" % (config.get_url(), "frontend_test_root_record")
        page = 1
        limit = 10
        start_Time = "2021-04-10 13:38:06"
        end_Time = ""
        key_word = "测试"
        res = requests.get(url, params=locals())
        data = res.content.decode("ascii")
        self.check(json.loads(data), key_word)

    def test_task_search_2(self):
        url = "%s/%s" % (config.get_url(), "frontend_test_root_record")
        page = 1
        limit = 10
        start_Time = "2021-04-10 13:38:06"
        end_Time = ""
        key_word = "528643"
        res = requests.get(url, params=locals())
        data = res.content.decode("ascii")
        self.check(json.loads(data), key_word)

    def test_task_search_3(self):
        url = "%s/%s" % (config.get_url(), "frontend_test_root_record")
        page = 1
        limit = 10
        start_Time = "2021-04-10 13:38:06"
        end_Time = ""
        key_word = "624988"
        res = requests.get(url, params=locals())
        data = res.content.decode("ascii")
        self.check(json.loads(data), key_word)


if __name__ == '__main__':
    unittest.main()
