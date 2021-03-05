"""调用树，monitor装饰器跟踪被监控代码时创建和维护"""


class IdNode:
    def __init__(self, parent_id, this_id, tag):
        self.parent = None
        self.this_id = this_id
        self.children = []
        self.tag = tag
        self.parent_id = parent_id

    def __repr__(self):
        return "%s<%s>"%(self.tag,self.this_id)


class IdTree:
    def __init__(self, parent_id, root_id,tag):
        self.root = IdNode(parent_id, root_id, tag, )

    def find(self,target_id):
        stack = [self.root]
        while stack:
            tmp = stack.pop(0)
            if tmp.this_id == target_id:
                return tmp
            else:
                stack.extend(tmp.children)
        else:
            return None

    @property
    def parent_id(self):
        return self.root.parent_id

    def append(self, parent_id, sub_id, tag=None):
        parent_node = self.find(parent_id)
        if not parent_node:
            raise Exception("parent not found")
        new_node = IdNode(parent_id, sub_id, tag)
        parent_node.children.append(new_node)
        new_node.parent = parent_node
        return new_node

    def append_tree(self, another_tree):  # 跨系统调用
        if not another_tree.parent_id:
            raise Exception("tree has no parent")
        attach_point = self.find(another_tree.parent_id)
        if not attach_point:
            raise Exception("parent not found")
        attach_point.children.append(another_tree._root)
        another_tree._root.parent = attach_point


if __name__ == "__main__":
    t = IdTree(None, "20200413004000_20201110232523_20201114112585", "root")
    # t.append("1","20200413004000_20201110232523_20201114112585",tag="main")
    t.append( "20200413004000_20201110232523_20201114112585", "1", tag="main")

    sub_tree  = IdTree("20200413004000_20201110232523_20201114112585","2",tag="main")
    sub_tree.append("2","12313",tag="A")
    sub_tree.append("2", "12314", tag="A")
    sub_tree.append("12314", "12315", tag="B")

    t.append_tree(sub_tree)
    pass



