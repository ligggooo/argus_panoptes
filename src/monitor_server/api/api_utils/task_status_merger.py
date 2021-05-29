#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : task_status_merger.py
# @Time      : 2021/4/14 16:37
# @Author    : Lee
from typing import Union, List, Tuple

from jiliang_process.process_monitor_types import ProcessState, StatePoint
from jiliang_process.status_track import StatusNode, StatusRecord
from jiliang_process.interfaces import StatusMergerInterface, GraphBlockInterface

if __name__ == "__main__":
    pass


class StatusMerger(StatusMergerInterface):
    def merge_info(self, records: List[StatusRecord]) -> Tuple[List[str], List[str]]:
        info = [r.desc for r in records if r.state!=ProcessState.failed.value and r.desc is not None and len(r.desc)]
        err = [r.desc for r in records if r.state == ProcessState.failed.value and r.desc is not None and len(r.desc)]
        return info, err

    def merge_status(self, records: List[StatusRecord]) -> Tuple[ProcessState, List[str], List[str], List[float],str]:
        '''
        Because original status records are generated when events of interests occur, so a task may have more than one
        record binded to it. To find out whether a task finishes or fails, this function must be called to merge records.
        :param records: related records
        :return: ProcessState
        '''
        info, err = self.merge_info(records)
        timestamps = [-1, -1]
        if len(records) == 0:
            err = ["尚无记录"]
            return ProcessState.not_started_yet, err, info, timestamps, ""
        if len(records) >= 1 and (not start_exists(records, timestamps)):
            err.insert(0, "记录不完整")
            return ProcessState.record_incomplete, err, info, timestamps, records[0].location
        if len(records) == 1 and start_exists(records, timestamps):
            return ProcessState.running, err, info, timestamps, records[0].location
        err_flag = error_exists(records, timestamps)
        if err_flag:
            info.insert(0, "任务存在报错")
            return ProcessState.failed, err, info, timestamps, records[0].location
        process_shutdown_flag, err_msg = process_shutdown(records, timestamps)
        if process_shutdown_flag:
            info.insert(0, "进程终止\n%s"%err_msg)
            return ProcessState.process_shutdown, err, info, timestamps, records[0].location
        if end_exists(records, timestamps):
            return ProcessState.finished, err, info, timestamps, records[0].location

    @staticmethod
    def build_graph_node(x: Union[StatusNode, None]):
        if x is None:
            block = GraphBlock(type='E', content="无记录", html_class="btn-default")
            block.parent_id = "-12"
            block.sub_id = "-12"
            return block
        if not isinstance(x, StatusNode):
            raise Exception("only build_graph_node(StatusNode)")
        success_num, error_num, total_num = x.sub_success_rate
        html_class = "btn-success" if success_num == total_num else "btn-warning"
        if x.status == ProcessState.failed:
            html_class = "btn-danger"
        if x.status == ProcessState.running:
            html_class = "btn-warning"
        block = GraphBlock(type='E', content=str(x), html_class=html_class)
        block.parent_id = x.parent_id
        block.sub_id = x.sub_id
        block.location = x.location
        return block


class GraphBlock(GraphBlockInterface):
    def __init__(self, type="N", content="", html_class=""):
        self.type = type
        self.content = content
        self.html_class = html_class


def start_exists(records: List[StatusRecord], time=None):
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
            return True
    return False


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
