"""任务跟踪器"""

import os
import json
import time
from functools import wraps
import traceback
import threading

import requests

from jiliang_process.jp_exceptions import ProcessIntentionallyShutDownException, ProcessShutDownException, \
    ProcessAccidentallyShutDownException
from .process_logger import get_logger, get_web_logger
from .call_track import IdTree
from .process_monitor_types import CallCategory, StatePoint
from .settings import TASK_UNIQUE_ID_URL


class ProcessMonitor:
    """
    任务跟踪器核心类
    """
    def __init__(self, sub_id=None, parent_id=None, web_logger=True):
        # self.sub_id = sub_id
        # self.parent_id = parent_id
        self.logger = get_web_logger() if web_logger else get_logger()
        self.unique_id_holder = UniqueId
        # self.index_holder = {}
        # self.normal_task_deco = self._normal_task()
        # self.loop_task_deco = self.loop_task()
        # self.concurrent_task_deco = self.concurrent_task()
        self.call_stack_tree = IdTree(parent_id, sub_id, tag="main")
        self.current_call_stack_node = None
        self.main_thread_id = threading.current_thread().ident
        self.root_id = None
        self.current_call_stack_node_dict = {self.main_thread_id: self.call_stack_tree.root}
        self.MONITOR_DISABLED = os.environ.get("MONITOR_ENABLED") is None

    def re_config(self, TASK_RECORDER_URL = "http://172.16.5.148:60010/record_tasks", TASK_UNIQUE_ID_URL = "http://172.16.5.148:60010/task_unique_id", MONITOR_DISABLED=False):
        self.logger.url = TASK_RECORDER_URL
        self.unique_id_holder.reset_url(TASK_UNIQUE_ID_URL)
        self.MONITOR_DISABLED = MONITOR_DISABLED

    def re_init(self, sub_id, parent_id, root_id, root_tag_name):
        # self.sub_id = sub_id
        # self.parent_id = parent_id
        self.root_id = root_id
        self.call_stack_tree = IdTree(parent_id, sub_id, tag=root_tag_name)
        self.current_call_stack_node_dict = {self.main_thread_id: self.call_stack_tree.root}

        # # 重置循环计数变量
        # for k in self.index_holder:
        #     self.index_holder[k] = 0
        # # 重置并发计数变量
        # Unique_id.reset()

    def get_current_call_stack_node(self):
        """
        获取调用线程当前执行栈节点 （非函数意义上的调用栈，而是被监控的过程栈）
        :return:
        """
        current_thread = threading.current_thread().ident
        current_call_stack_node = self.current_call_stack_node_dict.get(current_thread)
        if not current_call_stack_node:
            current_call_stack_node = self.current_call_stack_node_dict.get(self.main_thread_id)
            self.current_call_stack_node_dict[current_thread] = current_call_stack_node
        return current_call_stack_node

    def set_current_call_stack_node(self, node):
        """
        刷新调用线程当前执行栈节点
        :param node:
        :return:
        """
        current_thread = threading.current_thread().ident
        if current_thread not in self.current_call_stack_node_dict:
            raise Exception("this thread has not been registered")
        self.current_call_stack_node_dict[current_thread] = node

    def id_tree_grow(self, func, this_id):
        """
        当前线程调用了一个被监控的子过程，树生长
        :param func:
        :param this_id:
        :return:
        """
        # id树生长，指针下移
        parent_node = self.get_current_call_stack_node()
        parent_id = parent_node.this_id
        this_node_in_id_tree = self.call_stack_tree.append(parent_id, this_id, func.__name__)
        self.set_current_call_stack_node(this_node_in_id_tree)
        return parent_node, this_node_in_id_tree
        # id树生长 -------

    def normal_task_deco(self, name=None, show_kw_arg=None, show_position_arg=-1):
        """普通调用的装饰器"""

        @shorted_if(self.MONITOR_DISABLED)
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__ if name is None else name
                this_id = self.unique_id_holder.get()
                parent_node, this_node = self.id_tree_grow(func, this_id)  # 发起任务，id树生长，id树指针下移
                parent_id = parent_node.this_id
                desc = ""
                if show_kw_arg:
                    desc = "%s: %s" % (show_kw_arg, str(kwargs.get(show_kw_arg)))
                if show_position_arg >= 0 and show_position_arg < len(args):
                    desc = "arg_%d: %s" % (show_position_arg, str(args[show_position_arg]))

                self.logger.info(call_category=CallCategory.normal.value, sub_id=this_id,
                                 parent_id=parent_id,
                                 name=func_name, root_id=self.root_id,
                                 state=StatePoint.start.value, desc=desc)
                try:
                    res = func(*args, **kwargs)

                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.logger.info(call_category=CallCategory.normal.value, sub_id=this_id,
                                     parent_id=parent_id,
                                     name=func_name, root_id=self.root_id,
                                     state=StatePoint.error.value, desc=err_msg[-1000:])
                    # 任务失败 id树指针上移
                    self.set_current_call_stack_node(parent_node)
                    raise e
                self.logger.info(call_category=CallCategory.normal.value, sub_id=this_id,
                                 parent_id=parent_id,
                                 name=func_name, root_id=self.root_id,
                                 state=StatePoint.end.value, desc=desc)
                #   任务成功 id树指针上移
                self.set_current_call_stack_node(parent_node)
                return res

            return wrapper

        return deco

    def cross_thread_deco(self, name):
        """
        跨线程调用装饰器
        :param name:
        :return:
        """

        @shorted_if(self.MONITOR_DISABLED)
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__ if name is None else name
                this_id = self.unique_id_holder.get()
                parent_node, this_node = self.id_tree_grow(func, this_id)
                parent_id = parent_node.this_id
                print(threading.current_thread().ident, threading.current_thread().name)
                self.logger.info(call_category=CallCategory.cross_thread.value, sub_id=this_id,
                                 parent_id=parent_id, root_id=self.root_id,
                                 name=func_name,
                                 state=StatePoint.start.value)
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.logger.info(call_category=CallCategory.cross_thread.value, sub_id=this_id,
                                     parent_id=parent_id,
                                     name=func_name, root_id=self.root_id,
                                     state=StatePoint.error.value, desc=err_msg[-1000:])
                    # 任务失败 id树指针上移
                    self.set_current_call_stack_node(parent_node)
                    raise e
                self.logger.info(call_category=CallCategory.cross_thread.value, sub_id=this_id,
                                 parent_id=parent_id, root_id=self.root_id,
                                 name=func_name,
                                 state=StatePoint.end.value)
                # 任务完成 id树指针上移
                self.set_current_call_stack_node(parent_node)
                return res
            return wrapper
        return deco

    def cross_process_deco(self, name):
        """
        跨进程调用装饰器
        :param name:
        :return:
        """

        @shorted_if(self.MONITOR_DISABLED)
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__ if name is None else name
                parent_id, root_id = ProcessMonitor.make_connection_between_processes(kwargs)
                this_id = self.unique_id_holder.get()
                self.re_init(this_id, parent_id, root_id, func.__name__)
                # 任务拆分跨系统调用，需要用这种方式人工建立关联
                # self.id_tree_grow(func, this_id)
                self.logger.info(call_category=CallCategory.cross_process.value, sub_id=this_id,
                                 parent_id=parent_id, root_id=self.root_id,
                                 name=func_name,
                                 state=StatePoint.start.value)
                try:
                    res = func(*args, **kwargs)
                except ProcessAccidentallyShutDownException as e:
                    err_msg = str(e.msg)
                    self.logger.info(call_category=CallCategory.cross_process.value, sub_id=this_id,
                                     parent_id=parent_id,
                                     name=func_name, root_id=self.root_id,
                                     state=StatePoint.process_shutdown.value, desc=err_msg[-1000:])
                    # 任务意外自行退出 此子节点的所有子节点都需要在服务端关闭
                    self.current_call_stack_node = None
                    return e.data
                except ProcessIntentionallyShutDownException as e:
                    err_msg = str(e.msg)
                    self.logger.info(call_category=CallCategory.cross_process.value, sub_id=this_id,
                                     parent_id=parent_id,
                                     name=func_name, root_id=self.root_id,
                                     state=StatePoint.end.value, desc=err_msg[-1000:])
                    # 任务有意自行退出 此子节点的所有子节点都需要在服务端关闭
                    self.current_call_stack_node = None
                    return e.data
                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.logger.info(call_category=CallCategory.cross_process.value, sub_id=this_id,
                                     parent_id=parent_id,
                                     name=func_name, root_id=self.root_id,
                                     state=StatePoint.error.value, desc=err_msg[-1000:])
                    # 任务失败 此子进程直接退出，id树不需要再维护了
                    self.current_call_stack_node = None
                    raise e
                self.logger.info(call_category=CallCategory.cross_process.value, sub_id=this_id,
                                 parent_id=parent_id, root_id=self.root_id,
                                 name=func_name,
                                 state=StatePoint.end.value)
                return res
            return wrapper
        return deco

    def root_deco(self, name, root_tag_var_name=None):
        """
        根任务装饰器 多了一个创建任务的功能，所以logger需要多传一个root_tag
        :param name:
        :param root_tag_var_name:
        :return:
        """
        @shorted_if(self.MONITOR_DISABLED)
        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__ if name is None else name
                t = time.time()
                this_id = self.unique_id_holder.get()
                t1 = time.time()
                print("t1",t1-t)
                root_tag = ProcessMonitor.get_root_tag(kwargs, root_tag_var_name)
                if not root_tag:
                    root_tag = this_id
                self.re_init(sub_id=this_id, parent_id=None,
                             root_id=this_id, root_tag_name=func.__name__)
                # self.id_tree_grow(func, this_id)
                self.logger.info(call_category=CallCategory.root.value, sub_id=this_id,
                                 parent_id=None, root_id=self.root_id,
                                 name=func_name, root_tag=root_tag,
                                 state=StatePoint.start.value)
                t2 = time.time()
                print("t2", t2 - t1)
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.logger.info(call_category=CallCategory.root.value, sub_id=this_id,
                                     parent_id=None,
                                     name=func_name, root_id=self.root_id,
                                     state=StatePoint.error.value, desc=err_msg[-1000:])
                    # 任务失败 此子进程直接退出，id树不需要再维护了
                    self.current_call_stack_node = None
                    raise e
                self.logger.info(call_category=CallCategory.root.value, sub_id=this_id,
                                 parent_id=None, root_id=self.root_id,
                                 name=func_name,
                                 state=StatePoint.end.value)
                return res
            return wrapper
        return deco

    @staticmethod
    def make_connection_between_processes(in_dict):
        if ("parent_id" not in in_dict) or ("root_id" not in in_dict):
            raise Exception("跨进程调用接口必须提供（parent_id）(root_id)关键字参数，否则无法获得进程关系")
        else:
            return in_dict["parent_id"], in_dict["root_id"]

    @staticmethod
    def get_root_tag(in_dict, root_tag_var_name):
        if not root_tag_var_name:
            return None
        if root_tag_var_name not in in_dict:
            raise Exception("根任务标签必须是有效参数中的一个 %s " % in_dict.keys())
        return str(in_dict[root_tag_var_name])

    @property
    def current_id(self):
        return self.get_current_call_stack_node().this_id

    # def manual_log(self, id, state,desc="",name="root",root_id=None):
    #     self.logger.info(call_category=CallCategory.cross_process.value, sub_id=id,
    #                      parent_id=None,root_id=root_id,
    #                      name=name,desc= desc[-1000:],
    #                      state=state)

    def pack_monitor_params_into_str(self, str_params):
        print("packing monitor_params_into_str")
        try:
            params = json.loads(str_params)
        except Exception as e:
            raise e
        if "root_id" in params or "parent_id" in params:
            raise Exception("监控器客户端参数与原始参数冲突...")
        else:
            params.update({
                "root_id": self.root_id,
                "parent_id": self.current_id
            })
            return json.dumps(params)

    @staticmethod
    def extract_monitor_params_from_str(str_params):
        print("extracting monitor_params_from_str")
        try:
            params = json.loads(str_params)
        except Exception as e:
            raise e
        if "root_id" in params and "parent_id" in params:
            return params.get("root_id"), params.get("parent_id")
        else:
            raise Exception("监控器参数抽取失败...")


class UniqueId:
    """
        通过monitor后端的一个全局变量来模拟一个全局唯一id生成服务，最终可能通过更鲁棒的方式实现
    """

    _unique_id = 0
    _lock = threading.Lock()
    _id_url = TASK_UNIQUE_ID_URL

    @staticmethod
    def get():
        # with Unique_id._lock:
        #     ret = Unique_id._unique_id
        #     Unique_id._unique_id += 1
        # return ret
        res = requests.get(url=UniqueId._id_url)
        data = json.loads(res.content)
        u_id = data["task_unique_id"]
        return u_id

    @staticmethod
    def reset():
        UniqueId._unique_id = 0

    @staticmethod
    def reset_url(url):
        UniqueId._id_url = url


def shorted_if(flag):
    """
    这个装饰器可以使装饰器失效
    :param flag:
    :return:
    """
    if flag:
        def turn_into_null_deco(deco):
            def null_deco(func):
                return func
            return null_deco
        return turn_into_null_deco
    else:
        def do_nothing_to_deco(deco):
            return deco
        return do_nothing_to_deco

task_monitor = ProcessMonitor(sub_id="default", web_logger=True)
task_monitor.re_config()
task_monitor.deco_normal = task_monitor.normal_task_deco()
task_monitor.deco_root = task_monitor.root_deco("测试根")
task_monitor.deco_cross_p_merge = task_monitor.cross_process_deco("语义子任务根节点")
task_monitor.deco_normal_se_main = task_monitor.normal_task_deco("融合模块主函数")
