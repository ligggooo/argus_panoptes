from functools import wraps
from jiliang_process.process_logger import proc_mon_logger
import threading

def ProcessMonitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        proc_mon_logger.info("%s starts" % func.__name__)
        res = func(*args, **kwargs)
        proc_mon_logger.info("%s ends" % func.__name__)
        return res
    return wrapper

class Unique_id:
    _unique_id = 0
    _lock = threading.Lock()

    @staticmethod
    def get():
        with Unique_id._lock:
            ret = Unique_id._unique_id
            Unique_id._unique_id += 1
        return ret


def ProcessMonitor_Concurrent(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        this_id = Unique_id.get()
        proc_mon_logger.info("%s:%d starts" % (func.__name__, this_id))
        res = func(*args, **kwargs)
        proc_mon_logger.info("%s:%d ends" % (func.__name__,this_id))
        return res
    return wrapper


class ProcessMonitor_x:
    def __init__(self):
        pass