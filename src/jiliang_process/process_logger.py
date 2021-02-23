import logging
from logging import handlers
from logging.handlers import HTTPHandler as Hh
from logging import Formatter
import requests
from datetime import datetime
import json
import time

def get_logger(fname="test.log"):
    proc_mon_logger = logging.getLogger()
    proc_mon_logger.setLevel(logging.DEBUG)

    fh = logging.handlers.TimedRotatingFileHandler(filename=fname, encoding="utf-8")
    sh = logging.StreamHandler()

    fmt = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)

    proc_mon_logger.addHandler(fh)
    proc_mon_logger.addHandler(sh)
    return proc_mon_logger


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


def get_web_logger(url="http://127.0.0.1:60010/record_tasks"):
    proc_mon_logger = HttpLogger(url)
    return proc_mon_logger




if __name__ == "__main__":
    req = requests.get("http://127.0.0.1:60010/record_tasks",params={"msg":"123"})
    print(req.content.decode("utf-8"))