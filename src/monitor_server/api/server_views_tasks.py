import threading
from flask import Blueprint, request, url_for, render_template,json
import sys
# import json
import queue
from flask_apscheduler import APScheduler
from flask_cors import cross_origin

from jiliang_process.status_track import StatusRecord
from monitor_server.api.api_utils.db_utils import wake_up_data_base

sys.path.append("..")
from monitor_server.api.api_utils.clear_package import clear_package_name, clear_package_path

from jiliang_process.process_monitor_types import StatePoint
from monitor_server.models.model_006_tasks import Task, TaskTrackingRecord
from monitor_server import db
from monitor_server.api.api_utils.task_analysis import task_status_tree_cache

api_group5 = Blueprint("api_g5", __name__)

# ---------------------------------------------------------------------------------------------------------
# scheduler = APScheduler()
# # 定时任务周期性地读取数据库,将分析结果读入redis
# scheduler.add_job(func=load_records_to_redis, id="load_records_to_redis", args=(), trigger='interval',
#                   seconds=5, replace_existing=True)
# scheduler.start()
# # get_task 从redis中读取分析结果，呈现到前端
# ---------------------------------------------------------------------------------------------------------
scheduler = APScheduler()
# 定时任务周期性地读取数据库,保持数据库连接是活的
scheduler.add_job(func=wake_up_data_base, id="wake_up_data_base", args=(), trigger='interval',
                   seconds=50, replace_existing=True)
scheduler.start()
# # get_task 从redis中读取分析结果，呈现到前端
# ---------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------


@api_group5.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    root_id = request.args.get("root_id")
    parent_id = request.args.get("parent_id")
    sub_id = request.args.get("sub_id")

    test_url = url_for("api_g5.test_tasks")

    if not root_id:
        tasks = Task.query.order_by(Task.id.desc()).limit(4).all()

        for t in tasks:
            t.note = str(t)
            t.status, t.state_track, t.desc = task_status_tree_cache.get_status(root_id=t.root_id, parent_id=t.root_id)
            t.desc = t.desc.replace(" ", "&nbsp;").replace("\n", "<br>")
            for b in t.state_track:
                b.url = url_for("api_g5.get_tasks", root_id=t.root_id, sub_id=b.sub_id, parent_id=b.parent_id)
        return render_template("tasks.html", tasks=tasks, test_url=test_url, task_class="active")
    else:
        tasks,tree = task_status_tree_cache.get_tasks_from_cache(root_id=root_id, parent_id=parent_id, sub_id=sub_id)
        for t in tasks:
            t.note = str(t)
            t.desc = t.desc.replace(" ", "&nbsp;").replace("\n", "<br>")
            t.status, t.state_track, _ = task_status_tree_cache.get_status(root_id=root_id, parent_id=t.sub_id, tree=tree)
            for b in t.state_track:
                b.url = url_for("api_g5.get_tasks", root_id=t.root_id, sub_id=b.sub_id, parent_id=b.parent_id)
        return render_template("tasks.html", tasks=tasks, test_url=test_url, task_class="active")


@api_group5.route('/frontend_test_status_tree', methods=['GET', 'POST'])
@cross_origin()
def front_end_test():
    root_id = request.args.get("root_id")
    parent_id = request.args.get("parent_id")

    if not root_id:
        data = []
        tasks = Task.query.order_by(Task.id.desc()).limit(4).all()
        for t in tasks:
            t.note = str(t)
            tree_dump = task_status_tree_cache.get_tree_root_json_obj(root_id=t.root_id)
            size = sys.getsizeof(tree_dump)
            print(size)
            data.append(tree_dump)
    else:
        data = task_status_tree_cache.get_children_json_obj(root_id=root_id,parent_id=parent_id)
    res_json = json.dumps({
        "code": 200,
        "message": "请求成功",
        "data": data
    }, indent=" ")
    size = sys.getsizeof(res_json)
    print(size)
    return res_json


@api_group5.route('/record_tasks', methods=['POST', "GET"])
def record_tasks():
    from jiliang_process.process_monitor import CallCategory
    raw_data = request.values.get('msg')
    print(raw_data)
    data = json.loads(raw_data)
    if data.get("sub_id"):
        data["sub_id"] = str(data.get("sub_id"))
    if data.get("parent_id"):
        data["parent_id"] = str(data.get("parent_id"))
    if data.get("root_id"):
        data["root_id"] = str(data.get("root_id"))

    root_tag = "unknown "
    if "root_tag" in data:
        root_tag = data.pop("root_tag")
    new_task_track_obj = TaskTrackingRecord(**data)
    new_task_track_obj_shadow = StatusRecord(**data) # 不然会报错 orm对象非常讨厌
    print(new_task_track_obj)
    sess = db.session()
    sess.add(new_task_track_obj)
    task_status_tree_cache.update(new_task_track_obj_shadow)
    if new_task_track_obj.call_category == CallCategory.root.value and new_task_track_obj.state == StatePoint.start.value:
        new_task_obj = Task(name=data.get("name"), root_id=data.get("sub_id"), root_tag=root_tag, desc=data.get("desc"))
        sess.add(new_task_obj)
    try:
        sess.commit()
    except Exception as e:
        print(data)
        raise e
    sess.close()
    return "ok"


@api_group5.route('/tasks_start_test', methods=['POST'])
def test_tasks():
    from jiliang_process.pm_test import test_main
    import multiprocessing
    p = multiprocessing.Process(target=test_main, args=())
    p.start()
    msg = {"status": "success", "info": "测试任务已经启动"}
    return json.dumps(msg)


@api_group5.route('/task_unique_id', methods=['GET'])
def task_unique_id():
    from monitor_server.api.api_utils.task_id_system import g_task_unique_id
    id = g_task_unique_id.get_id()
    msg = {"task_unique_id": id}
    return json.dumps(msg)
