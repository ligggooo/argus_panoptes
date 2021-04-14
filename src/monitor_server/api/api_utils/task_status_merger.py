#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : task_status_merger.py
# @Time      : 2021/4/14 16:37
# @Author    : Lee
from typing import Union, List

from jiliang_process.process_monitor_types import ProcessState, StatePoint
from jiliang_process.status_track import StatusNode, StatusRecord

if __name__ == "__main__":
    pass


class StatusMerger:
    def merge_info(self, status, err, info):
        if "完成" in info:
            info_msg = "完成"
        elif "失败" in info:
            info_msg = "失败"
        elif "进程终止" in info:
            info_msg = "进程终止"
        else:
            info_msg = "running"
        err_msg = "\n".join(err)
        base_desc = "%s\n------------------\n%s"%(info_msg, err_msg)
        if status == ProcessState.running:
            desc = "%s" % base_desc
        elif status == ProcessState.finished:
            desc = "%s" % base_desc
        elif status == ProcessState.not_started_yet:
            desc = "尚未开始\n%s" % base_desc
        elif status == ProcessState.process_shutdown:
            desc = "进程退出\n%s" % err_msg
        else:
            desc = "错误\n%s" % base_desc
        return desc

    def merge_status(self, records, multi_task=False, regroup_index="index"):
        '''
        Because original status records are generated when events of interests occur, so a task may have more than one
        record binded to it. To find out whether a task finishes or fails, this function must be called to merge records.
        :param records: related records
        :return: ProcessState
        '''
        err = None
        info = None
        timestamps = [-1,-1]
        if len(records) == 0:
            err = "尚无记录"
            return ProcessState.not_started_yet, err, info, timestamps
        if len(records) >= 1 and (not start_exists(records)):
            err = "记录不完整"
            return ProcessState.record_incomplete, err, info, timestamps
        if len(records) == 1 and start_exists(records, timestamps):
            info = "running"
            return ProcessState.running, err, info, timestamps
        err_flag, err = error_exists(records, timestamps)
        if err_flag:
            info= "失败"
            return ProcessState.failed, err, info, timestamps
        process_shutdown_flag, err = process_shutdown(records, timestamps)
        if process_shutdown_flag:
            info = "进程终止"
            return ProcessState.process_shutdown, err, info, timestamps
        if end_exists(records, timestamps):
            info = "完成"
            err = None
            return ProcessState.finished, err, info, timestamps

    @staticmethod
    def build_graph_node(x: Union[StatusNode,None]):
        if x is None:
            block = GraphBlock(type='E', content="无记录", html_class="btn-default")
            block.parent_id = "-12"
            block.sub_id = "-12"
            return block
        if not isinstance(x, StatusNode):
            raise Exception("only build_graph_node(StatusNode)")
        success, total = x.sub_success_rate
        html_class = "btn-success" if success == total else "btn-warning"
        if x.status == ProcessState.failed:
            html_class = "btn-danger"
        if x.status == ProcessState.running:
            html_class = "btn-warning"
        block = GraphBlock(type='E', content=str(x), html_class=html_class)
        block.parent_id = x.parent_id
        block.sub_id = x.sub_id
        return block


class GraphBlock:
    def __init__(self, type="N", content="", html_class=""):
        self.type = type
        self.content = content
        self.html_class = html_class


def start_exists(records:List[StatusRecord],time=None):
    for r in records:
        if r.state == StatePoint.start.value:
            if time is not None:
                time[0] = r.timestamp
            return True
    return False


def error_exists(records, time=None):
    for r in records:
        if r.state == StatePoint.error.value:
            if time is not None:
                time[1] = r.timestamp
            return True, r.desc
    return False, ""


def process_shutdown(records, time=None):
    for r in records:
        if r.state == StatePoint.process_shutdown.value:
            if time is not None:
                time[1] = r.timestamp
            return True, r.desc
    return False, ""


def end_exists(records, time=None):
    for r in records:
        if r.state == StatePoint.end.value:
            if time is not None:
                time[1] = r.timestamp
            return True
    return False