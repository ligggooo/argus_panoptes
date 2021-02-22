from functools import wraps
from jiliang_process.process_logger import proc_mon_logger


def ProcessMonitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        proc_mon_logger.log("%s starts" % func.__name__)
        res = func(*args, **kwargs)
        proc_mon_logger.log("%s ends" % func.__name__)
        return res

    return wrapper

class ProcessMonitor_x:
    def __init__(self):
        pass