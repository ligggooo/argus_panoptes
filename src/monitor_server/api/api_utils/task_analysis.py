import sys

from monitor_server.api.api_utils.task_cache_system import TaskRecordCache, TaskStatusTreeCache
from monitor_server.api.api_utils.task_status_merger import StatusMerger
from monitor_server.settings.conf import config

sys.path.append("../../")
from monitor_server.models.model_006_tasks import TaskTrackingRecord, Task, db

import pickle
import os

from operation_utils.file import get_tmp_data_dir

_tmp_dir = get_tmp_data_dir()


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





# def get_records():
#     t_start = time.time() - 7 * 24 * 3600
#     tasks = Task.query.filter(Task.start_time >= t_start).order_by(Task.id.desc()).all()
#     records = {}
#     for t in tasks:
#         records[t.root_id] = get_task_records(t.root_id)
#     return records
#
#
# def get_records_for_test():
#     if config.TASK_TRACK_CACHE:
#         records = pickle.load(open(os.path.join(_tmp_dir, "task_record.dat"), 'rb'))
#     else:
#         records = get_records()
#     for root_id in records:
#         records = records[root_id]
#         return records


g_task_record_cache = TaskRecordCache(config.cache_size)
task_status_tree_cache = TaskStatusTreeCache(g_task_record_cache, StatusMerger())
task_status_tree_cache.load()  # 服务器启动的时候不存在线程竞争


if __name__ == "__main__":
    root_id_x = "832"
    # get_status(root_id=root_id)
    # get_status(root_id=root_id, parent_id="832")
    # s = get_status(sub_id="20200413004000_20201110232523_20201114112585", parent_id=None, tag="root")
    # print(s)

    pass
