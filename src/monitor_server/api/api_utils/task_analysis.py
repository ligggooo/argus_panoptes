import json
import sys
import threading
import time
from typing import Dict, Tuple, List

sys.path.append("../../")
from monitor_server.models.model_006_tasks import TaskTrackingRecord, Task, db

import pickle
import os

from jiliang_process.process_monitor_types import CallCategory, StatePoint, ProcessState
from jiliang_process.status_track import TaskStatusTree, StatusNode, StatusRecord
from operation_utils.file import get_tmp_data_dir, get_data_dir
from monitor_server.settings.conf import config

_tmp_dir = get_tmp_data_dir()


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


# def records_regroup(records):
#     '''
#     group according to index
#     :param records:
#     :return:
#     '''
#     res = {}
#     for r in records:
#         if index in res:
#             res[index].append(r)
#         else:
#             res[index] = [r]
#     return res


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


def load_records_to_redis():
    tasks = Task.query.order_by(Task.id.desc()).limit(6).all()
    records = {}
    print("load_records_to_redis")
    # raise Exception("load_records_to_redis")
    for t in tasks:
        # root_task_records = TaskTrackingRecord.query.filter_by(sub_id=t.root_id).all()
        task_records = TaskTrackingRecord.query.filter(TaskTrackingRecord.root_id == t.root_id).all()
        records[t.root_id] = task_records
    pickle.dump(records, open(os.path.join(_tmp_dir, "task_record.dat"), "wb"))
    db.session.commit()
    db.session.remove()
    return records


def get_task_records(root_id):
    task_records = TaskTrackingRecord.query.filter(TaskTrackingRecord.root_id == str(root_id)).all()
    return [t.freeze(safe=False) for t in task_records]


def get_records():
    t_start = time.time() - 7 * 24 * 3600
    tasks = Task.query.filter(Task.start_time >= t_start).order_by(Task.id.desc()).all()
    records = {}
    for t in tasks:
        records[t.root_id] = get_task_records(t.root_id)
    return records


def get_records_for_test():
    if config.TASK_TRACK_CACHE:
        records = pickle.load(open(os.path.join(_tmp_dir, "task_record.dat"), 'rb'))
    else:
        records = get_records()
    for root_id in records:
        records = records[root_id]
        return records


def build_graph_node(x: StatusNode):
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


"""
    ---------------------------------- 数据缓存 -----------------------------------
"""


class TaskRecordCache:
    """
    缓存内容会无限增加，得设计一个限制大小的机制
    LRU 就够了
    """
    # todo 进程共享需要尽快实现
    def __init__(self):
        self.records = {}
        self._lock = threading.Lock()

    def load(self):
        self.records = get_records()

    def clear(self):
        self.records = {}

    def insert(self, record):
        _root_id = str(record.root_id)
        with self._lock:
            if _root_id in self.records:
                self.records[_root_id].append(record)
            else:
                self.records[_root_id] = [record]

    def get_records(self, root_id):
        # todo 这样同步只能保证 root_id 存在，不能保证一个root_id对应的记录是一致完整的
        if root_id not in self.records:  # 缓存未命中
            with self._lock:
                if root_id not in self.records:  # dbl check
                    root_id_records = get_task_records(root_id)  # 到数据库里面查
                    if not root_id_records:
                        return None
                    else:
                        self.records[root_id] = root_id_records
                        return root_id_records
                else:
                    return self.records[root_id]
        else:
            return self.records[root_id]


class TaskStatusTreeCache:
    """
    缓存内容会无限增加，得设计一个限制大小的机制
    """

    def __init__(self, task_record_cache: TaskRecordCache):
        self._task_record_cache = task_record_cache
        self._trees: Dict[str, TaskStatusTree] = {}
        self._build_tree_lock = threading.Lock()

    def load(self):
        # todo 线程安全
        # 仅在服务器启动时调用，不必实现线程安全
        if not self._trees:
            self._task_record_cache.load()
            for root_id in self._task_record_cache.records:
                self._trees[root_id] = self.build_task_status_tree(root_id)

    def clear(self):
        self._task_record_cache.clear()
        self._trees = {}

    def find_tree_and_update(self, root_id):
        tree = self._trees.get(root_id)
        if not tree:
            return TaskStatusTree()
        tree.status_update(status_merger=StatusMerger())
        return tree

    def build_task_status_tree(self, root_id=None) -> TaskStatusTree:
        # todo 线程安全
        batch_records = self._task_record_cache.get_records(root_id)
        status_tree = TaskStatusTree.build_from_records(batch_records, status_merger=StatusMerger())
        return status_tree

    def get_status(self, root_id, parent_id=None, tag="root", tree:TaskStatusTree=None):
        # todo 线程安全
        if not tree:
            tree = self.find_tree_and_update(root_id)
        if not tree:
            return build_graph_node(None), [build_graph_node(None)], ""
        parent, children = tree.find_node_by_parent_id(parent_id)
        children.sort(key=lambda x: x.sub_id)
        # if not children:
        #     children = [tree.find_node_by_sub_id(parent_id)]
        #     parent = children[0]

        children_status_block = [build_graph_node(x) for x in children]
        parent_status_block = build_graph_node(parent)
        return parent_status_block, children_status_block, tree.root.desc

    def get_tree_root_json_obj(self, root_id):
        # todo 线程安全
        tree = self.find_tree_and_update(root_id)
        if not tree or not tree.root:
            return StatusNode.create_empty_node(root_id, root_id, root_id, str(root_id)).dump_without_children()
        res = tree.root.dump_without_children()
        return res

    def get_children_json_obj(self, root_id, parent_id, slice: Tuple[int, int]=None):
        # todo 线程安全
        tree = self.find_tree_and_update(root_id)
        parent, children = tree.find_node_by_parent_id(parent_id)
        children.sort(key=lambda x: x.sub_id)
        count = len(children)
        if slice:
            children = children[slice[0]:slice[1]]
        res = [c.dump_without_children() for c in children]
        return res,count

    def get_tasks_from_cache(self, root_id, parent_id=None, sub_id=None):
        # todo 线程安全
        tree = self.find_tree_and_update(root_id)
        if not tree:
            return None
        res = tree.find_node_by_sub_id(sub_id)
        return [res.copy()], tree

    def update(self, record):
        # todo 线程安全
        self._task_record_cache.insert(record)
        root_id = record.root_id
        tree_to_update = self._trees.get(root_id)
        if not tree_to_update:
            with self._build_tree_lock:
                tree_to_update = self._trees.get(root_id)
                if not tree_to_update:
                    self._trees[root_id] = self.build_task_status_tree(root_id)
        else:
            tree_to_update.update_with_record(record, StatusMerger())


g_task_record_cache = TaskRecordCache()
task_status_tree_cache = TaskStatusTreeCache(g_task_record_cache)
task_status_tree_cache.load() # 服务器启动的时候不存在线程竞争


if __name__ == "__main__":
    root_id_x = "832"
    # get_status(root_id=root_id)
    # get_status(root_id=root_id, parent_id="832")
    # s = get_status(sub_id="20200413004000_20201110232523_20201114112585", parent_id=None, tag="root")
    # print(s)

    pass
