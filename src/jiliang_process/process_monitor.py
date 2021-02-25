from functools import wraps
from jiliang_process.process_logger import get_logger,get_web_logger
from jiliang_process.call_track import IdTree
from jiliang_process.process_monitor_types import *
import threading
import traceback
import enum
import threading



class todo:
    def __init__(self, msg):
        self.msg = msg

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(self.msg)
            res = func(*args, **kwargs)
            return res
        return wrapper








class ProcessMonitor:
    def __init__(self, sub_id=None, parent_id=None, web_logger=True):
        # self.sub_id = sub_id
        # self.parent_id = parent_id
        self.logger = get_web_logger() if web_logger else get_logger()
        # self.index_holder = {}
        self.normal_task_deco = self._normal_task()
        # self.loop_task_deco = self.loop_task()
        # self.concurrent_task_deco = self.concurrent_task()
        self.call_stack_tree = IdTree(parent_id, sub_id, tag="main")
        self.current_call_stack_node = None
        self.main_thread_id = threading.current_thread().ident
        self.batch_id = None
        self.current_call_stack_node_dict = {self.main_thread_id: self.call_stack_tree._root}

    def _re_init(self,sub_id, parent_id, batch_id, root_tag_name):
        # self.sub_id = sub_id
        # self.parent_id = parent_id
        self.batch_id = batch_id
        self.call_stack_tree = IdTree(parent_id, sub_id, tag=root_tag_name)
        self.current_call_stack_node_dict = {self.main_thread_id: self.call_stack_tree._root}

        # # 重置循环计数变量
        # for k in self.index_holder:
        #     self.index_holder[k] = 0
        # # 重置并发计数变量
        # Unique_id.reset()

    def get_current_call_stack_node(self):
        current_thread = threading.current_thread().ident
        current_call_stack_node = self.current_call_stack_node_dict.get(current_thread)
        if not current_call_stack_node:
            current_call_stack_node = self.current_call_stack_node_dict.get(self.main_thread_id)
            self.current_call_stack_node_dict[current_thread] = current_call_stack_node
        return current_call_stack_node

    def set_current_call_stack_node(self,node):
        current_thread = threading.current_thread().ident
        if not current_thread in self.current_call_stack_node_dict:
            raise Exception("this thread has not been registered")
        self.current_call_stack_node_dict[current_thread] = node

    def id_tree_grow(self, func,this_id):
        # id树生长，指针下移
        parent_node = self.get_current_call_stack_node()
        parent_id = parent_node.this_id
        this_node_in_id_tree = self.call_stack_tree.append(parent_id, this_id, func.__name__)
        self.set_current_call_stack_node(this_node_in_id_tree)
        return parent_node,this_node_in_id_tree
        # id树生长 -------

    def _normal_task(self):
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                this_id = Unique_id.get()
                parent_node, this_node = self.id_tree_grow(func, this_id)
                parent_id = parent_node.this_id

                self.logger.info(call_category=CallCategory.normal.value, sub_id=this_id, parent_id=parent_id,
                                 name=func.__name__, batch_id=self.batch_id,
                                 state=StatePoint.start.value, desc="")
                try:
                    res = func(*args, **kwargs)

                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.logger.info(call_category=CallCategory.normal.value, sub_id=this_id, parent_id=parent_id,
                                     name=func.__name__, batch_id=self.batch_id,
                                     state=StatePoint.error.value, desc=err_msg[-1000:])
                    # 任务失败 id树指针上移
                    self.set_current_call_stack_node(parent_node)
                    raise e
                self.logger.info(call_category=CallCategory.normal.value, sub_id=this_id, parent_id=parent_id,
                                 name=func.__name__, batch_id=self.batch_id,
                                 state=StatePoint.end.value, desc="")
                #   任务成功 id树指针上移
                self.set_current_call_stack_node(parent_node)
                return res

            return wrapper

        return deco

    def cross_thread_deco(self, name):
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                this_id = Unique_id.get()
                parent_node, this_node = self.id_tree_grow(func, this_id)
                parent_id = parent_node.this_id
                print(threading.current_thread().ident, threading.current_thread().name)
                self.logger.info(call_category=CallCategory.cross_thread.value, sub_id=this_id,
                                 parent_id=parent_id,batch_id =self.batch_id,
                                 name=name,
                                 state=StatePoint.start.value)
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.logger.info(call_category=CallCategory.cross_thread.value, sub_id=this_id, parent_id=parent_id,
                                     name=name,batch_id =self.batch_id,
                                     state=StatePoint.error.value, desc=err_msg[-1000:])
                    # 任务失败 id树指针上移
                    self.set_current_call_stack_node(parent_node)
                    raise e
                self.logger.info(call_category=CallCategory.cross_thread.value, sub_id=this_id,
                                 parent_id=parent_id,batch_id =self.batch_id,
                                 name=name,
                                 state=StatePoint.end.value)
                # 任务完成 id树指针上移
                self.set_current_call_stack_node(parent_node)
                return res
            return wrapper
        return deco
        pass

    def cross_process_deco(self, name):
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                parent_id, batch_id = ProcessMonitor.get_parent_id(kwargs)
                this_id = Unique_id.get()
                self._re_init(this_id, parent_id,batch_id, func.__name__)  # 任务拆分跨系统调用，需要用这种方式人工建立关联
                self.id_tree_grow(func,this_id)
                self.logger.info(call_category=CallCategory.cross_process.value, sub_id=this_id,
                                 parent_id=parent_id, batch_id =self.batch_id,
                                 name=name,
                                 state=StatePoint.start.value)
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.logger.info(call_category=CallCategory.cross_process.value, sub_id=this_id, parent_id=parent_id,
                                     name=name,batch_id =self.batch_id,
                                     state=StatePoint.error.value, desc=err_msg[-1000:])
                    # 任务失败 此子进程直接退出，id树不需要再维护了
                    self.current_call_stack_node = None
                    raise e
                self.logger.info(call_category=CallCategory.cross_process.value, sub_id=this_id,
                                 parent_id=parent_id, batch_id =self.batch_id,
                                 name=name,
                                 state=StatePoint.end.value)
                return res
            return wrapper
        return deco

    @staticmethod
    def get_parent_id(in_dict):
        if ("parent_id" not in in_dict) or ("batch_id" not in in_dict):
            raise Exception("跨进程调用接口必须提供（parent_id）(batch_id)关键字参数，否则无法获得进程关系")
        else:
            return in_dict["parent_id"], in_dict["batch_id"]

    def manual_log(self, id, state,desc="",name="root",batch_id=None):
        self.logger.info(call_category=CallCategory.cross_process.value, sub_id=id,
                         parent_id=None,batch_id=batch_id,
                         name=name,desc= desc[-1000:],
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


task_monitor = ProcessMonitor(sub_id="default", web_logger=False)

