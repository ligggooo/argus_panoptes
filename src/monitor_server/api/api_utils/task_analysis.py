from models import TaskTrack, Task
from jiliang_process.process_monitor import CallCategory


def update_task_status():
    tasks = Task.query.all()
    # data = []
    for t in tasks:
        task_records = TaskTrack.query.filter_by(sub_id=t.task_id).all()
        sub_task_records = TaskTrack.query.filter_by(parent_id=t.task_id).all()
    pass


def get_status(sub_id="20200413004000_20201110232523_20201114112585", parent_id=None, tag="root"):
    status_graph = {
        "root": {
            "parent": None,
            "nodes": [(0, 0, 'root_s0'), (1, 1, 'root_s1')],
            'edges': [(0, 1, "main", CallCategory.cross_system)],
        },
        "main": {
            "parent": ("root","main",CallCategory.cross_system),
            "nodes": [(0, 0, 'main_s0'), (1, 1, 'main_s1'), (2, 2, 'main_s2'), (3, 3, 'main_s3')], # (index,group,node_tag)
            'edges': [(0, 1, "A", CallCategory.normal), (1, 2, "B", CallCategory.normal),
                      (2, 3, "C", CallCategory.normal)],  # (from,
            # to,edge_tag, how edge is called)
        },
        "B": {
            "parent": ("main", "B", CallCategory.normal),
        # (parent_graph, node_name_in_parent_graph, how_sub_graph_is_called)
            "nodes": [(0, 0, 'B_s0'), (1, 1, 'B_s1')],
            "edges": [(0, 1, "D", CallCategory.loop)],
        },
        "C": {
            "parent": ("main", "C"),
            "nodes": [(0, 0, 'C_s0'), (1, 1, 'C_s1')],
            "edges": [(0, 1, "E", CallCategory.concurrent)],
        }
    }



    class  GraphBlock:
        def __init__(self,type="N",content=""):
            self.type = type
            self.content = content

    state_track = {}
    if tag == "root":
        state_track = {
            "sub_id": "20200413004000_20201110232523_20201114112585",
            "parent_id": None,
            "root": True,
            "subtasks":{},
            "status":"finished",
        }
        for s_sub_id in [1,2,3]:
            state_track["subtasks"][(s_sub_id, sub_id)] = {"blocks": [GraphBlock("N","root_s0"),GraphBlock("E","main %s"%str(s_sub_id)),GraphBlock("N","root_s1")]}
    return state_track
