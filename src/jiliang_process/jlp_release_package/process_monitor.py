"""任务跟踪器的框架，用于和开发代码兼容"""
import traceback
from functools import wraps
import json


class EmptyProcessMonitor:
    boot_runner_available = False
    """
    任务跟踪器核心类的骨架
       为了减少对使用者的影响，EmptyProcessMonitor只提供根监控相关的参数检查功能，所有
       的监控装饰器都被短接
    """
    def __init__(self, sub_id=None, parent_id=None, web_logger=True):
        self.current_id = "empty_id"
        self.root_id = "empty_id"
        print("空的任务监控器初始化")

    def re_config(self, TASK_RECORDER_URL="http://172.16.5.148:60010/record_tasks",
                  TASK_UNIQUE_ID_URL="http://172.16.5.148:60010/task_unique_id",
                  MONITOR_DISABLED=False):
        """
        :param TASK_RECORDER_URL: 上传任务记录的url
        :param TASK_UNIQUE_ID_URL: 获取全局唯一id的url
        :param MONITOR_DISABLED:   监控器开关
        :return:
        """
        print("空的任务监控器配置")

    def normal_task_deco(self, name=None,show_position_arg=None):
        """普通调用的装饰器"""
        def deco(func):
            return func

        return deco

    def cross_thread_deco(self, name):
        """
        跨线程调用装饰器
        :param name:
        :return:
        """
        def deco(func):
            return func

        return deco


    def cross_process_deco(self, name):
        """
        跨进程调用装饰器
        :param name:
        :return:
        """
        def deco(func):
            @wraps(func)
            def check_parameters_wrapper(*args, **kwargs):
                parent_id, root_id = EmptyProcessMonitor.__make_connection_between_processes(kwargs)
                res = func(*args, **kwargs)
                return res
            return check_parameters_wrapper
        return deco

    def root_deco(self, name, root_tag_var_name=None):
        """
        根任务装饰器 多了一个创建任务的功能，所以logger需要多传一个root_tag
        :param name:
        :param root_tag_var_name:
        :return:
        """
        def deco(func):
            @wraps(func)
            def check_parameters_wrapper(*args, **kwargs):
                root_tag = self.__get_root_tag(kwargs, root_tag_var_name)
                res = func(*args, **kwargs)
                return res
            return check_parameters_wrapper
        return deco

    @staticmethod
    def __make_connection_between_processes(in_dict):
        if ("parent_id" not in in_dict) or ("root_id" not in in_dict):
            raise Exception("跨进程调用接口必须提供（parent_id）(root_id)关键字参数，否则监控器无法获得进程关系")
        else:
            return in_dict["parent_id"], in_dict["root_id"]

    @staticmethod
    def __get_root_tag(in_dict, root_tag_var_name):
        if not root_tag_var_name:
            return None
        if root_tag_var_name not in in_dict:
            raise Exception("根任务标签必须是有效参数中的一个 %s " % in_dict.keys())
        return str(in_dict[root_tag_var_name])

    @staticmethod
    def pack_monitor_params_into_str(str_params):
        try:
            params = json.loads(str_params)
        except Exception as e:
            err_msg = traceback.format_exc()
            raise Exception("json 解析失败，被打包的参数必须是json字符串\n%s" % err_msg)
        else:
            params.update({
                "root_id": "empty root_id",
                "parent_id": "empty parent_id"
            })
            return json.dumps(params)

    @staticmethod
    def extract_monitor_params_from_str(str_params):
        return "empty root_id","empty parent_id",str_params


def get_monitor(deploy_flag):
    if deploy_flag:
        import sys, os
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        jiliang_proc_path = os.path.join(root_path, "jiliang_monitor_pr", "src")
        sys.path.append(jiliang_proc_path)
        from jiliang_process.process_monitor import ProcessMonitor
        task_monitor = ProcessMonitor()
        task_monitor.re_config(TASK_RECORDER_URL="http://172.16.5.148:60010/record_tasks",
                  TASK_UNIQUE_ID_URL="http://172.16.5.148:60010/task_unique_id",
                  MONITOR_DISABLED=False)
    else:
        task_monitor = EmptyProcessMonitor()
    return task_monitor

import  os

if os.environ.get("MONITOR_ENABLED") is None:
    task_monitor = EmptyProcessMonitor()
    task_monitor.re_config()
    from deploy.jlp_release_package.jp_exceptions import ProcessAccidentallyShutDownException, \
        ProcessIntentionallyShutDownException, \
        ProcessShutDownException
else:
    task_monitor = get_monitor(deploy_flag=True)
    from jiliang_process.jp_exceptions import ProcessAccidentallyShutDownException, \
        ProcessIntentionallyShutDownException, \
        ProcessShutDownException