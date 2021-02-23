from functools import wraps
from jiliang_process.process_logger import get_logger,get_web_logger
import threading
import traceback
import enum


class StatePoint(enum.Enum):
    start = 0
    end = 1
    error = 2


class ProcessState(enum.Enum):
    record_incomplete = -2
    not_started_yet = -1
    running = 0
    # running_with_error = 0
    finished = 1
    # finished_with_error = 2
    failed = 2
    partially_finished = 3


class CallCategory(enum.Enum):
    root = -1
    normal = 0
    loop = 1
    concurrent = 2
    cross_system = 3
    branch = 4


class ProcessMonitor:
    def __init__(self, sub_id=None,parent_id=None):
        self.sub_id = sub_id
        self.parent_id = parent_id
        # self.logger = get_logger()
        self.logger = get_web_logger()
        self.index_holder = {}
        self.normal_task_deco = self.normal_task()
        self.loop_task_deco = self.loop_task()
        self.concurrent_task_deco = self.concurrent_task()

    def _re_init(self,sub_id=None, parent_id=None):
        self.sub_id = sub_id
        self.parent_id = parent_id
        # 重置循环计数变量
        for k in self.index_holder:
            self.index_holder[k] = 0
        # 重置并发计数变量
        Unique_id.reset()

    def normal_task(self):
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.info(call_category=CallCategory.normal.value, sub_id=self.sub_id, parent_id=self.parent_id, name=func.__name__,
                                 state=StatePoint.start.value, desc="")
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.logger.info(call_category=CallCategory.normal.value, sub_id=self.sub_id, parent_id=self.parent_id, name=func.__name__,
                                     state=StatePoint.error.value, desc=err_msg[-1000:])
                    raise e
                self.logger.info(call_category=CallCategory.normal.value, sub_id=self.sub_id, parent_id=self.parent_id, name=func.__name__,
                                 state=StatePoint.end.value, desc="")
                return res

            return wrapper

        return deco

    def loop_task(self):
        def deco(func):
            self.index_holder[func.__name__] = 0

            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.info(call_category=CallCategory.loop.value, sub_id=self.sub_id, parent_id=self.parent_id, name=func.__name__,
                                 state=StatePoint.start.value,
                                 index=self.index_holder[func.__name__])
                res = func(*args, **kwargs)
                self.logger.info(call_category=CallCategory.loop.value, sub_id=self.sub_id, parent_id=self.parent_id, name=func.__name__,
                                 state=StatePoint.end.value,
                                 index=self.index_holder[func.__name__])
                self.index_holder[func.__name__] += 1
                return res
            return wrapper
        return deco

    def concurrent_task(self):
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                this_id = Unique_id.get()
                self.logger.info(call_category=CallCategory.concurrent.value, sub_id=self.sub_id, parent_id=self.parent_id, name=func.__name__,
                                 state=StatePoint.start.value,
                                 index=this_id)
                res = func(*args, **kwargs)
                self.logger.info(call_category=CallCategory.concurrent.value, sub_id=self.sub_id, parent_id=self.parent_id, name=func.__name__,
                                 state=StatePoint.end.value,
                                 index=this_id)
                return res
            return wrapper
        return deco

    def cross_system_deco(self, name):
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                sub_id,parent_id = ProcessMonitor.get_id(kwargs)
                self._re_init(sub_id, parent_id)  # 任务拆分跨系统调用，需要用这种方式人工建立关联
                this_id = Unique_id.get()
                self.logger.info(call_category=CallCategory.cross_system.value, sub_id=self.sub_id,
                                 parent_id=self.parent_id,
                                 name=name,
                                 state=StatePoint.start.value)
                res = func(*args, **kwargs)
                self.logger.info(call_category=CallCategory.cross_system.value, sub_id=self.sub_id,
                                 parent_id=self.parent_id,
                                 name=name,
                                 state=StatePoint.end.value)
                return res
            return wrapper
        return deco

    @staticmethod
    def get_id(in_dict):
        if ("sub_id" not in in_dict) or ("parent_id" not in in_dict):
            raise Exception("main 函数必须包含sub_id和parent_id两个关键字参数")
        else:
            return in_dict["sub_id"], in_dict["parent_id"]

    def root_log(self, id, state,desc="",name="root"):
        self.logger.info(call_category=CallCategory.cross_system.value, sub_id=id,
                         parent_id=None,
                         name=name,
                         state=state)

class Unique_id:
    '''
    模拟一个全局的id服务，实际上可能通过redis实现
    '''
    _unique_id = 0
    _lock = threading.Lock()

    @staticmethod
    def get():
        with Unique_id._lock:
            ret = Unique_id._unique_id
            Unique_id._unique_id += 1
        return ret

    @staticmethod
    def reset():
        Unique_id._unique_id = 0

task_monitor = ProcessMonitor(sub_id="default")

