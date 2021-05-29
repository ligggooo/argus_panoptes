import json
import unittest
import requests
from models.model_003_machines import init_machines,Machine
from settings.conf import config

class MyTestCase(unittest.TestCase):
    def setUp(self):
        init_machines()
        self.machines = Machine.query.all()

    def test_init(self):
        pass # do nothing

    def test_del(self):
        url = "%s/%s" % (config.get_url(), "machines_del/")
        id = self.machines[0].id
        r = requests.delete(url, params={"id": "123"})
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content.decode("utf-8"))
        print(data)
        self.assertEqual(data["code"], 503)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data["message"], "failed")
        self.assertEqual(data["data"], "不存在此机器")

        for m in self.machines:
            id = m.id
            r = requests.delete(url, params={"id": id})
            self.assertEqual(r.status_code, 200)
            data = json.loads(r.content.decode("utf-8"))
            print(data)
            self.assertEqual(data["code"], 200)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(data["message"], "success")
            self.assertEqual(data["data"], "删除成功")
            self.assertTrue(Machine.query.filter(Machine.id==id).count()==0)
        self.assertTrue(Machine.query.count() == 0)

    def test_get(self):
        url = "%s/%s" % (config.get_url(), "get_machines/")





if __name__ == '__main__':
    unittest.main()
