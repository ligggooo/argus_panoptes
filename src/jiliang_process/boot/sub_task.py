#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : sub_task.py
# @Time      : 2021/3/25 13:53
# @Author    : Lee
from jiliang_process.jp_exceptions import ProcessIntentionallyShutDownException
from jiliang_process.process_monitor import task_monitor
import sys

@task_monitor.normal_task_deco()
def xx():
    raise ProcessIntentionallyShutDownException(12312, "12321")

@task_monitor.cross_process_deco("kua")
def main3(root_id, parent_id):
    xx()


if __name__ == "__main__":
    msg = sys.argv[1]
    print(msg)
    root_id, parent_id =task_monitor.extract_monitor_params_from_str(msg)
    main3(root_id=root_id, parent_id=parent_id)