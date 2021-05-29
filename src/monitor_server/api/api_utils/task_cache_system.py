#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : task_cache_system.py
# @Time      : 2021/4/14 11:14
# @Author    : Lee

"""
    ---------------------------------- 数据缓存 -----------------------------------
"""
import copy
import sqlalchemy
import sys
import threading
import time
import traceback
from abc import abstractmethod, ABC
from typing import Dict, Tuple, List, Any, Union
from concurrent.futures import ThreadPoolExecutor, Executor
from psycopg2.extras import execute_values

from monitor_server.api.api_utils.task_status_merger import StatusMerger
from monitor_server.models.model_006_tasks import TaskTrackingRecord, Task

sys.path.append("../../")

from jiliang_process.status_track import TaskStatusTree, StatusNode, StatusRecord


class NonDuplicatedDBLLinkListForLRU:
    """
    偷懒
    """

    def __init__(self, capacity):
        self._data: List[Any] = []
        self._lock = threading.Lock()
        self._capacity = capacity

    def add(self, item: Any):
        res = None
        with self._lock:
            if item in self._data:
                self._data.append(self._data.pop(self._data.index(item)))
            else:
                self._data.append(item)
            if len(self._data) > self._capacity:
                res = self._data.pop(0)
        return res

    def clear(self):
        self._data = []

    @property
    def keys(self):
        return self._data


class KeyedItem:
    def __init__(self, k):
        self.key = k
        self.val: Any = None

    def __repr__(self):
        return "<%s:%s>" % (self.key, self.val)

    def update(self, val):
        self.val = val


class KeyedStatusRecordList(KeyedItem):
    def __init__(self, k, records: List[StatusRecord]):
        super().__init__(k)
        self.val: List[StatusRecord] = records

    def update(self, val: List[StatusRecord]):
        self.val.extend(val)


class KeyedDataSrc(ABC):
    @abstractmethod
    def load(self, key: str) -> Union[KeyedItem, None]:
        return None

    @abstractmethod
    def write(self, items: List[Any]):
        time.sleep(10)

    def async_write(self, pool: Executor, items: List[Any]):
        pool.submit(self.write, items)


from settings.conf import config


class TaskTrackDbKeyedDataSrc(KeyedDataSrc):
    def __init__(self, conn_str):
        self.CONN_STR = conn_str

    def load(self, key: str) -> Union[KeyedItem, None]:
        task_records = TaskTrackingRecord.query.filter(TaskTrackingRecord.root_id == key).all()
        records = [t.freeze(safe=False) for t in task_records]
        item = KeyedStatusRecordList(key, records)
        return item

    def write(self, items: List[Any]):
        try:
            items = [item.to_tuple() for item in items]
            engine = sqlalchemy.create_engine(self.CONN_STR)
            cur = engine.raw_connection().cursor()
            if config.SQLALCHEMY_DATABASE_URI.startswith("postgresql"):
                execute_values(cur,
                               'INSERT INTO task_track (sub_id,parent_id,root_id,name,call_category,state,timestamp,"desc", location) VALUES %s',
                               items)
                cur.connection.commit()
            else:
                cur.executemany(
                    'INSERT INTO task_track (sub_id,parent_id,root_id,name,call_category,state,timestamp,"desc") VALUES %s',
                    items)
                cur.connection.commit()
            print(self.__class__, "done write, %d items" % len(items))
        except Exception as e:
            traceback.print_exc()
            raise e



class LRUCache(ABC):
    """
    LRU
    """

    def __init__(self, capacity: int, data_source):
        self._capacity: int = capacity
        self._hash_holder: Dict[str:KeyedItem] = {}
        self._linked_list_key_holder: NonDuplicatedDBLLinkListForLRU = NonDuplicatedDBLLinkListForLRU(capacity)
        self._slow_data_src: KeyedDataSrc = data_source
        self._lock = threading.RLock()

    def insert(self, item: Union[KeyedItem, None]):
        if item is None:
            return
        with self._lock:
            if item.key in self._hash_holder:
                self._hash_holder[item.key].update(item.val)
            else:
                self._hash_holder[item.key] = item
                key_to_delete = self._linked_list_key_holder.add(item.key)
                if key_to_delete:
                    self._hash_holder.pop(key_to_delete)

    def get(self, key: str):
        if key in self._hash_holder:
            return self._hash_holder.get(key).val
        else:
            with self._lock:
                # 防止等锁的过程中其他线程插入
                if key not in self._hash_holder:
                    item = self.load(key)
                    if item is not None:
                        self.insert(item)
                else:
                    item = self._hash_holder.get(key)
                return item.val

    @abstractmethod
    def flush(self):
        pass

    def load(self, key: str) -> Union[KeyedItem, None]:
        item = self._slow_data_src.load(key)
        return item

    # @abstractmethod
    # def load_all(self):
    #     pass

    def clear(self):
        self._hash_holder.clear()
        self._linked_list_key_holder.clear()

    def __repr__(self):
        return "\n".join([str(s) for s in self._hash_holder.items()])

    @property
    def keys(self):
        return self._linked_list_key_holder.keys


class TaskRecordCache(LRUCache):
    """
    任务记录缓存
    """

    # todo 进程共享需要尽快实现
    def __init__(self, capacity):
        super().__init__(capacity, TaskTrackDbKeyedDataSrc(config.SQLALCHEMY_DATABASE_URI))
        self.records = self._hash_holder
        self.writing_cache: List[StatusRecord] = []
        self._flush_limit = 1500
        self.async_pool = ThreadPoolExecutor(3)

    def clear(self):
        super().clear()
        self.records = {}

    def flush(self):
        with self._lock:
            tmp = copy.deepcopy(self.writing_cache)
            self.writing_cache.clear()
            self._slow_data_src.async_write(self.async_pool, tmp)

    def load_all(self):
        root_id_list = self.get_root_id_list_last_week()
        for root_id in root_id_list[-self._capacity:]:
            print("loading ... %s" % root_id)
            item = self.load(root_id)
            self.insert(item)
            print("loaded %s cnt = %d" % (root_id, len(item.val)))

    def insert_record(self, record: StatusRecord):
        item = KeyedStatusRecordList(record.root_id, [record])
        self.insert(item)
        self.writing_cache.append(record)
        if len(self.writing_cache) > self._flush_limit:
            with self._lock:
                if len(self.writing_cache) > self._flush_limit:
                    self.flush()

    @staticmethod
    def get_root_id_list_last_week():
        t_start = time.time() - 7 * 24 * 3600
        tasks = Task.query.filter(Task.start_time >= t_start).order_by(Task.start_time).all()
        root_id_list = [t.root_id for t in tasks]
        return root_id_list


class TaskStatusTreeCache:
    """
    缓存内容会无限增加，得设计一个限制大小的机制
    """

    def __init__(self, task_record_cache: TaskRecordCache, status_merger: StatusMerger):
        self._task_record_cache = task_record_cache
        self._trees: Dict[str, TaskStatusTree] = {}
        self._build_tree_lock = threading.Lock()
        self._status_merger = status_merger

    def flush_cache(self):
        self._task_record_cache.flush()

    def load(self):
        # todo 线程安全
        # 仅在服务器启动时调用，不必实现线程安全
        if not self._trees:
            self._task_record_cache.load_all()
            for root_id in self._task_record_cache.records:
                self._trees[root_id] = self.build_task_status_tree(root_id)

    def clear(self):
        self._task_record_cache.clear()
        self._trees = {}

    def find_tree_and_update(self, root_id):
        tree = self._trees.get(root_id)
        if not tree:
            return TaskStatusTree.create_empty_tree(root_id, tag=None)
        tree.status_update(self._status_merger)
        return tree

    def build_task_status_tree(self, root_id=None) -> TaskStatusTree:
        # todo 线程安全
        batch_records = self._task_record_cache.get(root_id)
        status_tree = TaskStatusTree.build_from_records(batch_records, status_merger=StatusMerger())
        return status_tree

    def get_status(self, root_id, parent_id=None, tag="root", tree: TaskStatusTree = None):
        # todo 线程安全
        if not tree:
            tree = self.find_tree_and_update(root_id)
        if not tree:
            return self._status_merger.build_graph_node(None), [self._status_merger.build_graph_node(None)], ""
        parent, children = tree.find_node_by_parent_id(parent_id)
        children.sort(key=lambda x: x.sub_id)
        # if not children:
        #     children = [tree.find_node_by_sub_id(parent_id)]
        #     parent = children[0]

        children_status_block = [self._status_merger.build_graph_node(x) for x in children]
        parent_status_block = self._status_merger.build_graph_node(parent)
        return parent_status_block, children_status_block, tree.root.desc

    def get_tree_root_json_obj(self, root_id):
        # todo 线程安全
        tree = self.find_tree_and_update(root_id)
        if not tree or not tree.root:
            return StatusNode.create_empty_node(root_id, root_id, root_id, str(root_id)).dump_without_children()
        res = tree.root.dump_without_children()
        return res

    def get_children_json_obj(self, root_id, parent_id, slice: Tuple[int, int] = None):
        # todo 线程安全
        tree = self.find_tree_and_update(root_id)
        parent, children = tree.find_node_by_parent_id(parent_id)
        children.sort(key=lambda x: x.sub_id)
        count = len(children)
        if slice:
            children = children[slice[0]:slice[1]]
        res = [c.dump_without_children() for c in children]
        return res, count

    def get_tasks_from_cache(self, root_id, parent_id=None, sub_id=None):
        # todo 线程安全
        tree = self.find_tree_and_update(root_id)
        if not tree:
            return None
        res = tree.find_node_by_sub_id(sub_id)
        return [res.copy()], tree

    def update(self, record):
        # todo 线程安全
        self._task_record_cache.insert_record(record)
        root_id = record.root_id
        tree_to_update = self._trees.get(root_id)
        if not tree_to_update:
            with self._build_tree_lock:
                tree_to_update = self._trees.get(root_id)
                if not tree_to_update:
                    self._trees[root_id] = self.build_task_status_tree(root_id)
        else:
            tree_to_update.update_with_record(record, StatusMerger())
