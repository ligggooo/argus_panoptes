from models.model_006_tasks import TaskTrackingRecord, Task
from jiliang_process.process_monitor import CallCategory,StatePoint,ProcessState
import pickle


class GraphBlock:
    def __init__(self, type="N", content=""):
        self.type = type
        self.content = content


class CoreNode:
    def __init__(self, cate, sub_id, parent_id, tag):
        self.cate = cate
        self.sub_id = sub_id
        self.parent_id = parent_id
        self.tag = tag

    def __repr__(self):
        return "%s:%s:%s:%s"%(self.tag, self.parent_id,self.sub_id,self.cate)


class SubGraphNode:
    def __init__(self, name, status_sub_graph, sub_id, parent_id,process_state=None,cate=None):
        if status_sub_graph:
            self.name = status_sub_graph.get("name", name)
            if not status_sub_graph.get("parent"):
                cate = CallCategory.root
            else:
                cate = status_sub_graph.get("parent")[2]
            self.edges = status_sub_graph.get("edges")
            self.nodes = status_sub_graph.get("nodes")
        else:
            self.name = name
            self.edges = []
            self.nodes = []
        self.node = CoreNode(cate, sub_id, parent_id, tag=self.name)
        self.process_state = process_state
        self.sub_graph = []
        self.parent = None

    def __repr__(self):
        return str(self.node)

    def update_edges(self, task_records, status_graph):
        for e_from, e_to, e_tag, e_cate in self.edges:
            status_sub_graph = status_graph.get(e_tag)
            if not status_sub_graph:
                sub_graph_name = e_tag
            else:
                sub_graph_name = status_sub_graph.get("name", e_tag)
            if e_cate == CallCategory.normal:
                records = list(filter(lambda x: (x.name == sub_graph_name and x.sub_id == self.node.sub_id),
                                      task_records["sub_task_records"]))
                task_status = merge_status(records)
                tmp_g_node = SubGraphNode(name=e_tag, status_sub_graph=status_sub_graph,
                                          sub_id=self.node.sub_id, parent_id=self.node.parent_id, process_state=task_status, cate=e_cate)
                tmp_g_node.parent = self
                self.sub_graph.append(tmp_g_node)
            elif e_cate == CallCategory.cross_system:
                records = list(filter(lambda x: x.name == sub_graph_name, task_records["sub_task_records"]))
                task_status = merge_status(records, multi_task=True, regroup_index="sub_id")
                for sub_id in task_status:
                    tmp_g_node = SubGraphNode(name=e_tag, status_sub_graph=status_sub_graph,
                                              sub_id=sub_id, parent_id=self.node.sub_id,
                                              process_state=task_status.get(sub_id),cate=e_cate)

                    tmp_g_node.parent = self
                    self.sub_graph.append(tmp_g_node)
            elif e_cate == CallCategory.loop or e_cate == CallCategory.concurrent:
                records = list(filter(lambda x: (x.name == sub_graph_name and x.sub_id == self.node.sub_id),
                                      task_records["sub_task_records"]))
                task_status = merge_status(records, multi_task=True, regroup_index="index")
                for sub_id in task_status:
                    tmp_g_node = SubGraphNode(name=e_tag, status_sub_graph=status_sub_graph,
                                              sub_id=sub_id, parent_id=self.node.parent_id,
                                              process_state=task_status.get(sub_id),cate=e_cate)

                    tmp_g_node.parent = self
                    self.sub_graph.append(tmp_g_node)

    def update(self, task_records, status_graph):
        if self.node.cate == CallCategory.root:
            records = task_records["task_records"]
            self.process_state = merge_status(records)
        self.update_edges(task_records,status_graph)

    # @property
    # def blocks(self):
    #
    #     return


status_graph = {
        "root": {
            "parent": None,
            "nodes": [(0, 0, 'root_s0'), (1, 1, 'root_s1')],
            'edges': [(0, 1, "main", CallCategory.cross_system)],
        },
        "main": {
            "name": "语义算法v 1.0.0",
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
            "parent": ("main", "C", CallCategory.normal),
            "nodes": [(0, 0, 'C_s0'), (1, 1, 'C_s1')],
            "edges": [(0, 1, "E", CallCategory.concurrent)],
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
            return True
    return False

def end_exists(records):
    for r in records:
        if r.state == StatePoint.end.value:
            return True
    return False


def records_regroup(records, regroup_index):
    '''
    group according to index
    :param records:
    :return:
    '''
    res = {}
    for r in records:
        index = getattr(r, regroup_index)
        if index in res:
            res[index].append(r)
        else:
            res[index] = [r]
    return res


def merge_status(records, multi_task = False, regroup_index="index"):
    '''
    Because original status records are generated when events of interests occur, so a task may have more than one
    record binded to it. To find out whether a task finishes or fails, this function must be called to merge records.
    :param records: related records
    :return: ProcessState
    '''
    if multi_task:
        records_rgp = records_regroup(records, regroup_index)
        res= {}
        for t_g_k in records_rgp:
            res[t_g_k] = merge_status(records_rgp[t_g_k], multi_task=False)
        return res
    if len(records) == 0:
        return ProcessState.not_started_yet
    if len(records) >= 1 and (not start_exists(records)):
        return ProcessState.record_incomplete
    if len(records) == 1 and start_exists(records):
        return ProcessState.running
    if error_exists(records):
        return ProcessState.failed
    if end_exists(records):
        return ProcessState.finished



def update_task_status():
    # tasks = Task.query.all()
    # data = {}
    # for t in tasks:
    #     task_records = TaskTrackingRecord.query.filter_by(sub_id=t.task_id).all()  # 目前只支持一次跨系统调用
    #     sub_task_records = TaskTrackingRecord.query.filter_by(parent_id=t.task_id).all()
    #     data[t.task_id] = {
    #         "task_records": task_records,
    #         "sub_task_records": sub_task_records
    #     }
    # pickle.dump(data,open("task_record.dat","wb"))

    data = pickle.load(open("task_record.dat", 'rb'))

    res = {}
    for k in data:
        task = data[k]  # 每个大任务是一棵独立的树
        root=None
        stack = []
        for g_tag in status_graph:
            # res['root'] = {"sub_id": "20200413004000_20201110232523_20201114112585", "parent_id": None, "root": True,
            #                    "subtasks": {"blocks": [GraphBlock("N", "root_s0"), GraphBlock("E", "main %d/%d" % (3, 4)),
            #                                            GraphBlock("N", "root_s1")]}, "status": "finished"}
            graph = status_graph[g_tag]
            if graph["parent"] is None:
                root = SubGraphNode(name='root', status_sub_graph=graph, sub_id=k, parent_id=None)
                stack.append(root)
                break
        while stack:
            sub_g_node = stack.pop(0)
            sub_g_node.update(task,status_graph)
            stack.extend(sub_g_node.sub_graph)

            #     pass
            # elif graph['parent'][2] == CallCategory.loop:
            #     sub_graph_name = graph.get("name", g_tag)
            #     records = list(filter(lambda x: x.name == sub_graph_name, task["sub_task_records"]))
            #     if records:
            #         task_status = merge_status(records, multi_task=True, regroup_index="index")
            #     pass
            # elif graph['parent'][2] == CallCategory.concurrent:
            #     sub_graph_name = graph.get("name", g_tag)
            #     records = list(filter(lambda x: x.name == sub_graph_name, task["sub_task_records"]))
            #     if records:
            #         task_status = merge_status(records, multi_task=True, regroup_index="index")
            #     pass
            # elif graph['parent'][2] == CallCategory.normal:
            #     sub_graph_name = graph.get("name", g_tag)
            #     records = list(filter(lambda x: x.name == sub_graph_name, task["sub_task_records"]))
            #     if records:
            #         task_status = merge_status(records, multi_task=False)
            #     pass

    return root

def get_status(sub_id="20200413004000_20201110232523_20201114112585", parent_id=None, tag="root"):
    state_track = {}
    res = update_task_status()
    if tag == "root":
        state_track = res['root']
        # for s_sub_id in [1,2,3]:

    elif tag=="main":
        state_track = res["main"]
    return state_track


if __name__ == "__main__":
    update_task_status()
    s = get_status()
    print(s)