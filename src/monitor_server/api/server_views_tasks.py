import threading
from flask import Blueprint, request, url_for, render_template
import sys
import json
from flask_apscheduler import APScheduler

from jiliang_process.status_track import StatusRecord

sys.path.append("..")
from api.api_utils.clear_package import clear_package_name, clear_package_path
from api.api_utils.task_analysis import get_status, get_tasks_from_redis, load_records_to_redis,task_record_cache

from jiliang_process.process_monitor_types import StatePoint
from models.model_006_tasks import Task, TaskTrackingRecord
from monitor_server import db

api_group5 = Blueprint("api_g5", __name__)

# scheduler = APScheduler()
# # 定时任务周期性地读取数据库,将分析结果读入redis
# scheduler.add_job(func=load_records_to_redis, id="load_records_to_redis", args=(), trigger='interval',
#                   seconds=5, replace_existing=True)
# scheduler.start()
# # get_task 从redis中读取分析结果，呈现到前端




@api_group5.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    root_id = request.args.get("root_id")
    parent_id = request.args.get("parent_id")
    sub_id = request.args.get("sub_id")

    test_url = url_for("api_g5.test_tasks")

    if not root_id:
        tasks = Task.query.order_by(Task.id.desc()).limit(10).all()

        for t in tasks:
            t.note = str(t)
            t.state_track, t.desc = get_status(root_id=t.root_id, parent_id=t.root_id)
            for b in t.state_track:
                b.url = url_for("api_g5.get_tasks", root_id=t.root_id, sub_id=b.sub_id, parent_id=b.parent_id)
        return render_template("tasks.html", tasks=tasks, test_url=test_url)
    else:
        tasks,tree = get_tasks_from_redis(root_id=root_id, parent_id=parent_id, sub_id=sub_id)
        for t in tasks:
            t.note = str(t)
            t.desc = t.desc.replace(" ", "&nbsp;").replace("\n", "<br>")
            t.state_track, _ = get_status(root_id=root_id, parent_id=t.sub_id, tree=tree)
            for b in t.state_track:
                b.url = url_for("api_g5.get_tasks", root_id=t.root_id, sub_id=b.sub_id, parent_id=b.parent_id)
        return render_template("tasks.html", tasks=tasks, test_url=test_url)


@api_group5.route('/record_tasks', methods=['POST', "GET"])
def record_tasks():
    from jiliang_process.process_monitor import CallCategory
    raw_data = request.values['msg']
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
    task_record_cache.insert(new_task_track_obj_shadow)
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
