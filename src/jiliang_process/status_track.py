import copy
import json

from jiliang_process.process_monitor_types import ProcessState,StatePoint
from typing import List,Tuple
'''
class TaskTrackingRecord(db.Model):
    __tablename__ = "task_track"
    __table_args__ = ()
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sub_id = db.Column(db.String(128), nullable=False, unique=False)
    parent_id = db.Column(db.String(128), nullable=True, unique=False)
    root_id = db.Column(db.String(128), nullable=False, unique=False)
    name = db.Column(db.String(128), nullable=False, unique=False)
    call_category = db.Column(db.Integer, nullable=False, unique=False)
    state = db.Column(db.Integer, nullable=False, unique=False)
    timestamp = db.Column(db.Float, nullable=False, unique=False)
    desc = db.Column(db.String(1024), nullable=True, unique=False)
'''


class StatusRecord:
    # 模仿适配flask ORM对象
    def __init__(self, sub_id=None,
                 parent_id=None,
                 root_id=None,
                 name=None,
                 call_category=None,
                 state=None,
                 timestamp=None,
                 desc=None):
        self.id = None
        self.sub_id = sub_id
        self.parent_id = parent_id
        self.root_id = root_id
        self.name = name
        self.call_category = call_category
        self.state = state
        self.timestamp = timestamp
        self.desc = desc

    def generate_fake_end_record(self):
        "生成一条假的结束记录"
        fake_record = copy.deepcopy(self)
        fake_record.state = StatePoint.process_shutdown.value
        return fake_record


class StatusNode:
    def __init__(self, root_id, parent_id, sub_id, tag):
        self.parent = None
        self.children = []
        self.parent_id = parent_id
        self.sub_id = sub_id
        self.root_id = root_id
        self.tag = tag
        self.records: List[StatusRecord] = []
        self.start_time = -1
        self.end_time = -1
        self.status = ProcessState.unknown  # 节点日志中反映出的完成情况
        self.sub_success_rate = [0, 0]  # 子节点日志中反映出的完成情况( 完成数/总数 )
        self.err = set()
        self.info = set()
        self.desc = None
        self.ended_signature = None  # 为了手动关闭节点而增加的标记

    def __repr__(self):
        return "%s<%s>%s<%d/%d>" % (
            self.tag, self.sub_id, self.status.name, self.sub_success_rate[0], self.sub_success_rate[1])

    @staticmethod
    def create_node_from_record(record):
        new_node = StatusNode(record.root_id, record.parent_id, record.sub_id, record.name)
        new_node.records.append(record)
        return new_node

    def copy(self):
        cp = StatusNode(self.root_id, self.parent_id, self.sub_id, self.tag)
        cp.status = self.status
        cp.sub_success_rate = self.sub_success_rate.copy()
        cp.desc = self.desc
        return cp

    def close_sub_nodes(self):
        """
        特殊需求，关闭子节点
        :return:
        """
        for c in self.children:
            if len(c.records) >0 and not c.ended_signature:
                fake_record = c.records[0].generate_fake_end_record()
                c.records.append(fake_record)
                c.ended_signature = True # 标记过一次就不会再标记了

    def dump(self, res):
        res.update({
            "id": self.sub_id,
            "success_rate": self.sub_success_rate,
            "tag": self.tag,
            "err": list(self.err),
            "info": list(self.info),
            "status":self.status.name,
            "children":[{} for c in self.children]
        })
        for i,c in enumerate(self.children):
            c.dump(res["children"][i])
        return res

    def dump_without_children(self):
        return {
            "id": self.sub_id,
            "success_rate": self.sub_success_rate,
            "tag": self.tag,
            "err": list(self.err),
            "info": list(self.info),
            "status": self.status.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "has_children": len(self.children) > 0
        }

class TaskStatusTree:
    def __init__(self):
        self.root:StatusNode = None
        self.orphans = []
        self.records = []
        self.node_cache = {}

    def cache_node(self, new_node):
        if new_node.sub_id in self.node_cache:
            raise Exception("缓存逻辑错误")
        self.node_cache[new_node.sub_id] = new_node

    # 这个方法也简单粗暴，可以加速 todo
    # 方案一： 缓存
    def find_node_by_sub_id_old(self, sub_id):
        stack = [self.root]
        while stack:
            tmp = stack.pop(0)
            if tmp.sub_id == sub_id:
                return tmp
            else:
                if tmp.sub_id < sub_id:  # 若当前节点的id大于待查id，则没必要继续查找了
                    stack.extend(tmp.children)
        else:
            return None

    def find_node_by_sub_id(self, sub_id):
        return self.node_cache.get(sub_id)

    def find_node_by_parent_id(self, parent_id)->Tuple[StatusNode, List[StatusNode]]:
        if parent_id is None:
            return None, [self.root]
        parent_node = self.find_node_by_sub_id(parent_id)
        if not parent_node:
            return None, []
        else:
            return parent_node, parent_node.children

    def add_node(self, new_node, parent_id, new_node_gurantee_flag=False):
        if self.root is None:
            self.root = new_node
            self.cache_node(new_node)
            return True
        else:
            if not new_node_gurantee_flag: # 若无法保证这个是新节点，就查一次
                this_node = self.find_node_by_sub_id(new_node.sub_id)
                if this_node:  # 这个node是某个节点的另一个记录
                    this_node.records.extend(new_node.records)
                    return True
            node_to_attach_to = self.find_node_by_sub_id(parent_id)
            if not node_to_attach_to:
                # 可能这个节点更高级
                if self.root.parent_id == new_node.sub_id:
                    new_node.children.append(self.root)
                    self.cache_node(new_node)
                    self.root.parent = new_node
                    self.root = new_node
                    return True
                elif self.root.sub_id == new_node.sub_id:
                    # 可能这个节点就是根节点的另一个记录
                    self.root.records.extend(new_node.records)
                    return True
                else:
                    # 两个节点无关联
                    self.orphans.append(new_node)
                    return False
                # raise Exception("cannot find parent node to attach <%s> to"%new_node)  # todo  如果中间记录丢失怎么办？
            else:
                node_to_attach_to.children.append(new_node)
                new_node.parent = node_to_attach_to
                self.cache_node(new_node)
                return True

    def add_record(self, record):
        res = True
        self.records.append(record)
        if not self.root:
            self.add_node(StatusNode.create_node_from_record(record),parent_id=None)
        else:
            node = self.find_node_by_sub_id(record.sub_id)
            if not node:
                new_node = StatusNode.create_node_from_record(record)
                status = self.add_node(new_node, new_node.parent_id, new_node_gurantee_flag=True)
                if not status:  # 说明记录添加失败，记录作为orphan被添加到树的孤儿列表了
                    res = False
            else:
                node.records.append(record)
        return res

    def consume_orphans(self):
        len_orphans = len(self.orphans)
        cnt = 0
        while self.orphans:  # 说明没有添加完
            tmp_node = self.orphans.pop(0)
            self.add_node(tmp_node, tmp_node.parent_id)
            if len_orphans > len(self.orphans):  # 说明有点被加入了
                len_orphans = len(self.orphans)
                cnt = 0
            else:
                cnt += 1
            if cnt > 0 and cnt > len_orphans:
                self.root.err.add("存在记录丢失，调用树被割裂")
                break

    def status_update(self, status_merger):
        # 后续遍历树,刷新每个节点的状态
        # 目前每次都重来一遍，以后规模增加之后可以做进一步优化
        stack = [self.root]
        stack_rev = []
        while stack:
            tmp = stack.pop()
            tmp.sub_success_rate = [0, 0]
            info_msg = None
            try:
                tmp.status, err_msg, info_msg = status_merger.merge_status(tmp.records)
                if tmp.status == ProcessState.process_shutdown:  # 一个特殊情况，启动进程的进程发现子进程结束
                    # 目前的策略是： 在这个地方关掉所有的子节点
                    tmp.close_sub_nodes()
            except Exception as e:
                print(e)
                err_msg = str(e)
            if err_msg is not None:
                tmp.err.add(err_msg)
            if info_msg is not None:
                tmp.info.add(info_msg)
            tmp.desc = status_merger.merge_info(tmp.status, tmp.err, tmp.info)

            # if desc and tmp.desc and desc != tmp.desc:
            #     tmp.desc = tmp.desc + " | \n " + desc
            # else:
            #     if desc:
            #         tmp.desc = desc
            stack_rev.append(tmp)
            if tmp.children:
                stack.extend(tmp.children)
        for node in reversed(stack_rev):  # 从后往前，先序遍历，刷新
            if not node.children:
                if node.status == ProcessState.finished:
                    node.sub_success_rate = [1, 1]
                else:
                    node.sub_success_rate = [0, 1]
            if not node.parent:
                continue
            node.parent.sub_success_rate[1] += 1
            if node.sub_success_rate[0] == node.sub_success_rate[1] and node.status == ProcessState.finished:
                node.parent.sub_success_rate[0] += 1

    @staticmethod
    def build_from_records(records, status_merger):
        t = TaskStatusTree()
        if not records:
            return None
        records = sorted(records, key=lambda x: x.sub_id)
        for r in records:
            t.add_record(r)
            print(len(t.records),len(t.orphans))

        # 可能存在记录顺序不对导致有些节点没有找到父节点
        # todo 此方法太简单粗暴，应该优化  建树过程应该允许分段进行
        t.consume_orphans()

        t.status_update(status_merger)
        return t

    def update_with_record(self, record, status_merger):
        self.add_record(record)
        self.status_update(status_merger)

    def dumps(self):
        res = {}
        self.root.dump(res)
        return res

if __name__ == "__main__":
    txx = TaskStatusTree()
    from monitor_server.api.api_utils.task_analysis import get_records_for_test

    records = get_records_for_test()
    for r in records:
        txx.add_record(r)
        pass
    pass
