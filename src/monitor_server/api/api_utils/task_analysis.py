import sys
import threading

sys.path.append("../../")
from models.model_006_tasks import TaskTrackingRecord, Task, db

import pickle
import os

from jiliang_process.process_monitor_types import CallCategory, StatePoint, ProcessState
from jiliang_process.status_track import TaskStatusTree, StatusNode
from operation_utils.file import get_tmp_data_dir, get_data_dir
from monitor_server.settings.conf import config

_tmp_dir = get_tmp_data_dir()


class GraphBlock:
    def __init__(self, type="N", content="", html_class=""):
        self.type = type
        self.content = content
        self.html_class = html_class


status_graph = {
    "root": {
        "parent": None,
        "nodes": [(0, 0, 'root_s0'), (1, 1, 'root_s1')],
        'edges': [(0, 1, "main", CallCategory.cross_process)],
    },
    "main": {
        "name": "语义算法v 1.0.0",
        "parent": ("root", "main", CallCategory.cross_process),
        "nodes": [(0, 0, 'main_s0'), (1, 1, 'main_s1'), (2, 2, 'main_s2'), (3, 3, 'main_s3')],
        'edges': [(0, 1, "A", CallCategory.normal), (1, 2, "B", CallCategory.normal),
                  (2, 3, "C", CallCategory.normal)],  # (from,to,edge_tag, how edge is called)
    },
    "B": {
        "parent": ("main", "B", CallCategory.normal),
        # (parent_graph, node_name_in_parent_graph, how_sub_graph_is_called)
        "nodes": [(0, 0, 'B_s0'), (1, 1, 'B_s1')],
        "edges": [(0, 1, "D", CallCategory.normal)],
    },
    "C": {
        "parent": ("main", "C", CallCategory.normal),
        "nodes": [(0, 0, 'C_s0'), (1, 1, 'C_s1')],
        "edges": [(0, 1, "E", CallCategory.cross_process)],
    }
}


def start_exists(records):
    for r in records:
        if r.state == StatePoint.start.value:
            return True
    return False


def error_exists(records):
    for r in records:
        if r.state == StatePoint.error.value:
            return True, r.desc
    return False, ""


def end_exists(records):
    for r in records:
        if r.state == StatePoint.end.value:
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


def merge_status(records, multi_task=False, regroup_index="index"):
    '''
    Because original status records are generated when events of interests occur, so a task may have more than one
    record binded to it. To find out whether a task finishes or fails, this function must be called to merge records.
    :param records: related records
    :return: ProcessState
    '''
    desc = ""
    if len(records) == 0:
        desc = "尚无记录"
        return ProcessState.not_started_yet, desc
    if len(records) >= 1 and (not start_exists(records)):
        desc = "记录不完整"
        return ProcessState.record_incomplete, desc
    if len(records) == 1 and start_exists(records):
        desc = "running"
        return ProcessState.running, desc
    error, desc = error_exists(records)
    if error:
        return ProcessState.failed, desc
    if end_exists(records):
        desc = "完成"
        return ProcessState.finished, desc


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
    tasks = Task.query.order_by(Task.id.desc()).limit(10).all()
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


def build_task_status_tree(root_id=None):
    batch_records = task_record_cache.get_records(root_id)
    status_tree = TaskStatusTree.build_from_records(batch_records, status_merger=merge_status)
    return status_tree


def build_graph_node(x):
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


def get_status(root_id, parent_id=None, tag="root", tree=None):
    if not tree:
        tree = build_task_status_tree(root_id)
    if not tree:
        return [build_graph_node(None)]
    parent, children = tree.find_node_by_parent_id(parent_id)
    children.sort(key=lambda x: x.sub_id)
    if not children:
        chilren = [tree.find_node_by_sub_id(parent_id)]
        parent = chilren[0]

    chilren_status_block = [build_graph_node(x) for x in children]
    parent_status_block = build_graph_node(parent)
    return parent_status_block,chilren_status_block, tree.root.desc


def get_tasks_from_redis(root_id, parent_id=None, sub_id=None):
    tree = build_task_status_tree(root_id)
    if not tree:
        return None
    res = tree.find_node_by_sub_id(sub_id)
    return [res], tree


class TaskRecordCache:
    """
    缓存内容会无限增，得设计一个限制大小的机制
    """

    def __init__(self):
        self.records = {}
        self._lock = threading.Lock()

    def load(self):
        self.records = get_records()

    def insert(self, record):
        _root_id = str(record.root_id)
        if _root_id in self.records:
            self.records[_root_id].append(record)
        else:
            self.records[_root_id] = [record]

    def get_records(self, root_id):
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


task_record_cache = TaskRecordCache()
task_record_cache.load()

if __name__ == "__main__":
    root_id = "832"
    # get_status(root_id=root_id)
    # get_status(root_id=root_id, parent_id="832")
    # s = get_status(sub_id="20200413004000_20201110232523_20201114112585", parent_id=None, tag="root")
    # print(s)
    get_task_records(1120)
    tc = TaskRecordCache()
    tc.load()
    xx = tc.get_records(1120)
    pass
