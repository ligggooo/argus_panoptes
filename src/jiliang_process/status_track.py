

'''
class TaskTrackingRecord(db.Model):
    __tablename__ = "task_track"
    __table_args__ = ()
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sub_id = db.Column(db.String(128), nullable=False, unique=False)
    parent_id = db.Column(db.String(128), nullable=True, unique=False)
    batch_id = db.Column(db.String(128), nullable=False, unique=False)
    name = db.Column(db.String(128), nullable=False, unique=False)
    call_category = db.Column(db.Integer, nullable=False, unique=False)
    state = db.Column(db.Integer, nullable=False, unique=False)
    timestamp = db.Column(db.Float, nullable=False, unique=False)
    desc = db.Column(db.String(1024), nullable=True, unique=False)
'''

class StatusRecord:
    # 模仿适配falsk ORM对象
    def __init__(self):
        self.id = None
        self.sub_id = None
        self.parent_id = None
        self.batch_id = None
        self.name = None
        self.call_category = None
        self.state = None
        self.timestamp = None
        self.desc = None


class StatusNode:
    def __init__(self, parent_id, sub_id, tag):
        self.parent = None
        self.children = []
        self.parent_id = parent_id
        self.sub_id = sub_id
        self.tag = tag
        self.records = []
        self.status = None

    def __repr__(self):
        return "%s<%s>%s"%(self.tag,self.sub_id,self.status)

    @staticmethod
    def create_node_from_record(record):
        new_node = StatusNode(record.parent_id, record.sub_id, record.name)
        new_node.records.append(record)
        return new_node


class TaskStatusTree:
    def __init__(self):
        self.root = None

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
            return self.root
        parent_node = self.find_node_by_sub_id(parent_id)
        if not parent_id:
            return []
        else:
            return parent_node.children

    def add_node(self, new_node, parent_id):
        if self.root is None:
            self.root = new_node
        else:
            node_to_attach_to = self.find_node_by_sub_id(parent_id)
            if not node_to_attach_to:
                raise Exception("cannot find parent node to attach <%s> to"%new_node)
            else:
                node_to_attach_to.children.append(new_node)

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
    def build_from_records(records,status_merger):
        t = TaskStatusTree()
        for r in records:
            t.add_record(r)
        stack = [t.root]
        while stack:
            tmp = stack.pop(0)
            tmp.status = status_merger(tmp.records)
            if len(tmp.children) >0:
                stack.extend(tmp.children)
        return t

if __name__ == "__main__":
    t = TaskStatusTree()
    from monitor_server.api.api_utils.task_analysis import get_records_for_test
    records = get_records_for_test()
    for r in records:
        t.add_record(r)
        pass
    pass

