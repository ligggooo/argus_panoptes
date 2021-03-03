from models.model_006_tasks import TaskTrackingRecord, Task, db
from jiliang_process.process_monitor import CallCategory,StatePoint,ProcessState
from jiliang_process.status_track import TaskStatusTree,StatusNode
import pickle
from operation_utils.file import get_tmp_data_dir,get_data_dir
import os

_tmp_dir = get_tmp_data_dir()

class GraphBlock:
    def __init__(self, type="N", content="",html_class=""):
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
            "parent": ("root","main",CallCategory.cross_process),
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


def merge_status(records, multi_task = False, regroup_index="index"):
    '''
    Because original status records are generated when events of interests occur, so a task may have more than one
    record binded to it. To find out whether a task finishes or fails, this function must be called to merge records.
    :param records: related records
    :return: ProcessState
    '''
    desc = ""
    if len(records) == 0:
        return ProcessState.not_started_yet,desc
    if len(records) >= 1 and (not start_exists(records)):
        return ProcessState.record_incomplete,desc
    if len(records) == 1 and start_exists(records):
        return ProcessState.running,desc
    error,desc = error_exists(records)
    if error:
        return ProcessState.failed, desc
    if end_exists(records):
        return ProcessState.finished,desc


def load_records_to_redis():
    tasks = Task.query.order_by(Task.id.desc()).limit(6).all()
    records = {}
    print("load_records_to_redis")
    # raise Exception("load_records_to_redis")
    for t in tasks:
        # root_task_records = TaskTrackingRecord.query.filter_by(sub_id=t.task_id).all()
        task_records = TaskTrackingRecord.query.filter(TaskTrackingRecord.batch_id==t.task_id).all()
        records[t.task_id] = task_records
    pickle.dump(records, open(os.path.join(_tmp_dir,"task_record.dat"), "wb"))
    db.session.commit()
    db.session.remove()
    return records

def get_records_for_test():
    records = pickle.load(open(os.path.join(_tmp_dir,"task_record.dat"), 'rb'))
    # records = get_records()
    for batch_id in records:
        records = records[batch_id]
        return records

def build_task_status_tree():
    records = pickle.load(open(os.path.join(_tmp_dir,"task_record.dat"), 'rb'))
    # records = get_records()
    res = {}
    for batch_id in records:
        batch_records = records[batch_id]
        status_tree = TaskStatusTree.build_from_records(batch_records, status_merger=merge_status)
        res[batch_id] = status_tree
    return res


def build_graph_node(x):
    if x is None:
        block = GraphBlock(type='E', content="无记录", html_class="btn-default")
        block.parent_id = "-12"
        return block
    if not isinstance(x, StatusNode):
        raise Exception("only build_graph_node(StatusNode)")
    success,total = x.sub_success_rate
    html_class = "btn-success" if success==total else "btn-warning"
    if x.status == ProcessState.failed:
        html_class = "btn-danger"
    block = GraphBlock(type='E',content=str(x),html_class=html_class)
    block.parent_id = x.parent_id
    return block

def get_status(batch_id, parent_id=None, tag="root"):
    tree = build_task_status_tree().get(batch_id)
    if not tree:
        return [build_graph_node(None)]
    res = tree.find_node_by_parent_id(parent_id)
    if not res:
        res = [tree.find_node_by_sub_id(parent_id)]

    res2 = [build_graph_node(x) for x in res]
    return res2

def get_tasks_from_redis(batch_id, parent_id=None):
    tree = build_task_status_tree().get(batch_id)
    if not tree:
        return None
    res = tree.find_node_by_parent_id(parent_id)
    return res

if __name__ == "__main__":
    batch_id = "20200413004000_20201110232523_20201114112585"
    get_status(batch_id=batch_id)
    get_status(parent_id=batch_id)
    # s = get_status(sub_id="20200413004000_20201110232523_20201114112585", parent_id=None, tag="root")
    # print(s)