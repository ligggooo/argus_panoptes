import datetime
import sys, time

from flask import Blueprint, request, url_for, render_template, json
# import json
from flask_apscheduler import APScheduler
from flask_cors import cross_origin

from jiliang_process.status_track import StatusRecord
from monitor_server.api.api_utils.db_utils import wake_up_data_base

sys.path.append("..")
from monitor_server import db
from jiliang_process.process_monitor_types import StatePoint, CallCategory
from monitor_server.models.model_006_tasks import Task, TaskTrackingRecord
from monitor_server.api.api_utils.task_id_system import g_task_unique_id
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
# scheduler = APScheduler()
# # 定时任务周期性地读取数据库,保持数据库连接是活的
# scheduler.add_job(func=wake_up_data_base, id="wake_up_data_base", args=(), trigger='interval',
#                    seconds=50, replace_existing=True)
# scheduler.start()
# # get_task 从redis中读取分析结果，呈现到前端
# ---------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------


@api_group5.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    root_id = request.args.get("root_id")
    parent_id = request.args.get("parent_id")
    sub_id = request.args.get("sub_id")

    test_url = url_for("api_g5.test_tasks")
    #  缓存同步，目前刷新逻辑是满了才同步，所以要找个地方手动触发没满的那一部分
    task_status_tree_cache.flush_cache()

    if not root_id:
        tasks = Task.query.order_by(Task.id.desc()).limit(4).all()

        for t in tasks:
            t.note = str(t)
            t.status, t.state_track, t.desc = task_status_tree_cache.get_status(root_id=t.root_id, parent_id=t.root_id,
                                                                                tag=t.name)
            t.desc = t.desc.replace(" ", "&nbsp;").replace("\n", "<br>")
            for b in t.state_track:
                b.url = url_for("api_g5.get_tasks", root_id=t.root_id, sub_id=b.sub_id, parent_id=b.parent_id)
        return render_template("tasks.html", tasks=tasks, test_url=test_url, task_class="active")
    else:
        tasks, tree = task_status_tree_cache.get_tasks_from_cache(root_id=root_id, parent_id=parent_id, sub_id=sub_id)
        for t in tasks:
            t.note = str(t)
            t.desc = t.desc.replace(" ", "&nbsp;").replace("\n", "<br>")
            t.status, t.state_track, _ = task_status_tree_cache.get_status(root_id=root_id, parent_id=t.sub_id,
                                                                           tree=tree)
            for b in t.state_track:
                b.url = url_for("api_g5.get_tasks", root_id=t.root_id, sub_id=b.sub_id, parent_id=b.parent_id)
        return render_template("tasks.html", tasks=tasks, test_url=test_url, task_class="active")


@api_group5.route('/frontend_test_record', methods=['GET'])
@cross_origin()
def front_end_test():
    root_id = request.args.get("root_id")
    parent_id = request.args.get("id")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    data, count = task_status_tree_cache.get_children_json_obj(root_id=root_id, parent_id=parent_id,
                                                               slice=((page - 1) * limit, page * limit))
    res_json = json.dumps({
        "code": 200,
        "message": "请求成功",
        "data": {
            "count": count,
            "data": data
        }
    }, indent=" ")
    size = sys.getsizeof(res_json)
    print(size)
    return res_json


@api_group5.route('/frontend_test_root_record', methods=['GET'])
@cross_origin()
def frontend_test_root_record():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    start_Time = request.args.get("start_Time")
    end_Time = request.args.get("end_Time")
    data = []

    tasks = Task.query
    if start_Time:
        tasks = tasks.filter(Task.start_time >= time.mktime(time.strptime(start_Time, "%Y-%m-%d %H:%M:%S")))
    if end_Time:
        tasks = tasks.filter(Task.start_time <= time.mktime(time.strptime(end_Time, "%Y-%m-%d %H:%M:%S")))
    if not start_Time and not end_Time:
        t_start = time.time() - 7 * 24 * 3600
        tasks = tasks.filter(Task.start_time >= t_start)
    tasks = tasks.order_by(Task.start_time.desc())
    count = tasks.count()
    tasks = tasks.slice((page - 1) * limit, page * limit).all()

    for t in tasks:
        t.note = str(t)
        tree_dump = task_status_tree_cache.get_tree_root_json_obj(root_id=t.root_id)
        size = sys.getsizeof(tree_dump)
        print(size)
        data.append(tree_dump)

    res_json = json.dumps({
        "code": 200,
        "message": "请求成功",
        "data": {
            "count": count,
            "data": data
        }
    }, indent=" ")
    size = sys.getsizeof(res_json)
    print(size)
    return res_json


@api_group5.route('/record_tasks', methods=['POST', "GET"])
def record_tasks():
    raw_data = request.values.get('msg')
    print(raw_data)
    data = json.loads(raw_data)
    recorder_tasks_doer(data)
    return "ok"


def recorder_tasks_doer(data):
    if data.get("sub_id"):
        data["sub_id"] = str(data.get("sub_id"))
    if data.get("parent_id"):
        data["parent_id"] = str(data.get("parent_id"))
    if data.get("root_id"):
        data["root_id"] = str(data.get("root_id"))

    root_tag = "unknown "
    if "root_tag" in data:
        root_tag = data.pop("root_tag")
    # new_task_track_obj = TaskTrackingRecord(**data)
    new_task_track_obj_shadow = StatusRecord(**data)  # 不然会报错 orm对象非常讨厌
    # print(new_task_track_obj)
    sess = db.session()
    # sess.add(new_task_track_obj)
    task_status_tree_cache.update(new_task_track_obj_shadow)
    # todo 线程不安全
    # todo 不能能跨进程共享
    # todo 将树状态刷新操作从这个update中移除，放到某一个响应时间不敏感的接口中去。
    if new_task_track_obj_shadow.call_category == CallCategory.root.value and new_task_track_obj_shadow.state == StatePoint.start.value:
        new_task_obj = Task(name=data.get("name"), root_id=data.get("sub_id"), root_tag=root_tag,
                            desc=data.get("desc"), start_time=data.get("timestamp"), end_time=-1)
        sess.add(new_task_obj)
    if new_task_track_obj_shadow.call_category == CallCategory.root.value and new_task_track_obj_shadow.state != StatePoint.start.value:
        tasks = Task.query.filter(Task.root_id == data.get("sub_id")).limit(1).all()
        if len(tasks) > 0:
            task = tasks[0]
            task.end_time = data.get("timestamp")
            task.desc = StatePoint(int(data.get("state"))).name
            sess.add(task)
    try:
        sess.commit()
    except Exception as e:
        print(data)
        raise e
    sess.close()


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
    id = g_task_unique_id.get_id()
    msg = {"task_unique_id": id}
    return json.dumps(msg)


@api_group5.route('/slow_job', methods=['POST'])
def slow_job_post_endpoint():
    print(request.data)
    return "ok"


@api_group5.route('/post_test_write_db', methods=['POST'])
def post_test_write_db():
    content = request.data.decode("utf-8")
    print(content)
    sess = db.session()
    from monitor_server.models.model_001_test import Info
    info = Info(content=content[:4096])
    sess.add(info)
    sess.commit()
    sess.close()
    return "ok"
