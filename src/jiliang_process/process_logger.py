"""logger 模块 自定义了一个web logger"""

import logging
import requests
import json
import time
import sys
import os


from .process_monitor_types import CallCategory, StatePoint
from .settings import TASK_RECORDER_URL


class MyFileLogger:
    """
    文件logger
    """
    def __init__(self, file_name):
        self.logger = logging.getLogger("jiliang_process_logger")
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(filename=file_name, encoding="utf-8")
        sh = logging.StreamHandler(sys.stdout)

        fmt = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        fh.setFormatter(fmt)
        sh.setFormatter(fmt)

        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

    def info(self, **kwargs):
        kwargs["state"] = StatePoint(kwargs.get("state")).name
        kwargs["call_category"] = CallCategory(kwargs.get("call_category")).name
        # {"call_category": "normal", "sub_id": 3, "parent_id": 1,
        #  "name": "normal_task_sleeps", "root_id": null,
        #  "state": "start", "desc": ""}
        msg = "{0} {1}".format(kwargs["name"], kwargs["state"])
        # msg = json.dumps(kwargs)
        self.logger.info(msg)


class HttpLogger:
    """
        文件logger
    """
    def __init__(self, url):
        proc_mon_logger = logging.getLogger("jiliang_process_logger")
        proc_mon_logger.setLevel(logging.INFO)
        sh = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        sh.setFormatter(fmt)
        proc_mon_logger.addHandler(sh)
        self.logger = proc_mon_logger
        self.url = url

    def info(self, **kwargs):
        # msg = self.logger.makeRecord()
        location = "%s,%s"%(os.environ.get("HOST_IP", "unknown"), os.environ.get("CONTAINER_NAME","unknown"))
        kwargs.update({"timestamp":time.time(), "location": location})
        msg = json.dumps(kwargs)
        self.logger.info(msg)
        # tc = datetime.utcnow().strftime("%Y%m%d_%H:%M:%S.%f")[:-3]
        # msg = "%s %s"%(tc, msg)
        try:
            requests.post(self.url, data={"msg":msg})
        except requests.exceptions.ConnectTimeout as e:
            self.logger.info(str(e))
        except Exception as e:
            print(e)


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
