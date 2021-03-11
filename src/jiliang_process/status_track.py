from jiliang_process.process_monitor_types import ProcessState

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
    # 模仿适配falsk ORM对象
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


class StatusNode:
    def __init__(self, root_id, parent_id, sub_id, tag):
        self.parent = None
        self.children = []
        self.parent_id = parent_id
        self.sub_id = sub_id
        self.root_id = root_id
        self.tag = tag
        self.records = []
        self.status = ProcessState.unknown  # 节点日志中反映出的完成情况
        self.sub_success_rate = [0, 0]  # 子节点日志中反映出的完成情况( 完成数/总数 )
        self.desc = None

    def __repr__(self):
        return "%s<%s>%s<%d/%d>" % (
        self.tag, self.sub_id, self.status.name, self.sub_success_rate[0], self.sub_success_rate[1])

    @staticmethod
    def create_node_from_record(record):
        new_node = StatusNode(record.root_id, record.parent_id, record.sub_id, record.name)
        new_node.records.append(record)
        return new_node


class TaskStatusTree:
    def __init__(self):
        self.root = None
        self.orphans = []

    def find_node_by_sub_id(self, sub_id):
        stack = [self.root]
        while stack:
            tmp = stack.pop(0)
            if tmp.sub_id == sub_id:
                return tmp
            else:
                stack.extend(tmp.children)
        else:
            return None

    def find_node_by_parent_id(self, parent_id):
        if parent_id is None:
            return [self.root]
        parent_node = self.find_node_by_sub_id(parent_id)
        if not parent_node:
            return None,[]
        else:
            return parent_node,parent_node.children

    def add_node(self, new_node, parent_id):
        if self.root is None:
            self.root = new_node
        else:
            this_node = self.find_node_by_sub_id(new_node.sub_id)
            if this_node:  # 这个node是某个节点的另一个记录
                this_node.records.extend(new_node.records)
                return
            node_to_attach_to = self.find_node_by_sub_id(parent_id)
            if not node_to_attach_to:
                # 可能这个节点更高级
                if self.root.parent_id == new_node.sub_id:
                    new_node.children.append(self.root)
                    self.root.parent = new_node
                    self.root = new_node
                elif self.root.sub_id == new_node.sub_id:
                    # 可能这个节点就是根节点的另一个记录
                    self.root.records.extend(new_node.records)
                else:
                    # 两个节点无关联
                    self.orphans.append(new_node)
                # raise Exception("cannot find parent node to attach <%s> to"%new_node)  # todo  如果中间记录丢失怎么办？
            else:
                node_to_attach_to.children.append(new_node)
                new_node.parent = node_to_attach_to

    def add_record(self, record):
        if not self.root:
            self.root = StatusNode.create_node_from_record(record)
        else:
            node = self.find_node_by_sub_id(record.sub_id)
            if not node:
                new_node = StatusNode.create_node_from_record(record)
                self.add_node(new_node, new_node.parent_id)
            else:
                node.records.append(record)

    @staticmethod
    def build_from_records(records, status_merger):
        t = TaskStatusTree()
        if not records:
            return None
        for r in records:
            t.add_record(r)
        len_orphans = len(t.orphans)
        cnt = 0
        while t.orphans:  # 说明没有添加完
            tmp_node = t.orphans.pop(0)
            t.add_node(tmp_node, tmp_node.parent_id)
            if len_orphans > len(t.orphans):  # 说明有点被加入了
                len_orphans = len(t.orphans)
                cnt = 0
            else:
                cnt += 1
            if cnt > 0 and cnt > len_orphans:
                t.root.desc = "存在记录丢失，调用树被割裂"
                break

        # 后续遍历树
        stack = [t.root]
        stack_rev = []
        while stack:
            tmp = stack.pop()
            tmp.status, desc = status_merger(tmp.records)
            if desc and tmp.desc:
                tmp.desc = tmp.desc + " | \n " + desc
            else:
                if desc:
                    tmp.desc = desc
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
            if node.sub_success_rate[0] == node.sub_success_rate[1]:
                node.parent.sub_success_rate[0] += 1
        return t


if __name__ == "__main__":
    t = TaskStatusTree()
    from monitor_server.api.api_utils.task_analysis import get_records_for_test

    records = get_records_for_test()
    for r in records:
        t.add_record(r)
        pass
    pass
