"""logger 模块 自定义了一个web logger"""

import logging
import requests
import json
import time

from .process_monitor_types import *
from .settings import TASK_RECORDER_URL


class MyFileLogger:
    def __init__(self, file_name):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(filename=file_name, encoding="utf-8")
        sh = logging.StreamHandler()

        fmt = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        fh.setFormatter(fmt)
        sh.setFormatter(fmt)

        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

    def info(self, **kwargs):
        kwargs["state"] = StatePoint(kwargs.get("state")).name
        kwargs["call_category"] = CallCategory(kwargs.get("call_category")).name
        # {"call_category": "normal", "sub_id": 3, "parent_id": 1, "name": "normal_task_sleeps", "root_id": null,
        #  "state": "start", "desc": ""}
        msg = "{0} {1}".format(kwargs["name"],kwargs["state"])
        # msg = json.dumps(kwargs)
        self.logger.info(msg)


class HttpLogger:
    def __init__(self, url):
        proc_mon_logger = logging.getLogger()
        proc_mon_logger.setLevel(logging.INFO)
        sh = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        sh.setFormatter(fmt)
        proc_mon_logger.addHandler(sh)
        self.logger = proc_mon_logger
        self.url = url

    def info(self, **kwargs):
        # msg = self.logger.makeRecord()
        kwargs.update({"timestamp":time.time()})
        msg = json.dumps(kwargs)
        self.logger.info(msg)
        # tc = datetime.utcnow().strftime("%Y%m%d_%H:%M:%S.%f")[:-3]
        # msg = "%s %s"%(tc, msg)
        requests.post(self.url, data={"msg":msg})


def get_web_logger(url=TASK_RECORDER_URL):
    proc_mon_logger = HttpLogger(url)
    return proc_mon_logger


def get_logger(fname="test.log"):
    logger = MyFileLogger(fname)
    return logger

if __name__ == "__main__":
    # req = requests.get("http://127.0.0.1:60010/record_tasks",params={"msg":"123"})
    # print(req.content.decode("utf-8"))
    x = get_logger()
    pass