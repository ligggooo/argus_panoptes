from flask import Blueprint,request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from api.api_utils.task_analysis import get_status, get_tasks_from_redis, load_records_to_redis
from models.model_006_tasks import Task,TaskTrackingRecord
from monitor_server import db
from flask_apscheduler import APScheduler


api_group5 = Blueprint("api_g5",__name__)

scheduler = APScheduler()
# 定时任务周期性地读取数据库,将分析结果读入redis
scheduler.add_job(func=load_records_to_redis, id="load_records_to_redis", args=(), trigger='interval',
                  seconds=5, replace_existing=True)
scheduler.start()
# get_task 从redis中读取分析结果，呈现到前端

@api_group5.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    batch_id = request.args.get("batch_id")
    parent_id = request.args.get("parent_id")

    test_url = url_for("api_g5.test_tasks")

    if not batch_id:
        tasks = Task.query.order_by(Task.id.desc()).limit(5).all()

        for t in tasks:
            t.state_track = get_status(batch_id=t.task_id,parent_id=t.task_id)
            for b in t.state_track:
                b.url = url_for("api_g5.get_tasks",batch_id=t.task_id,parent_id=b.parent_id)
        return render_template("tasks.html", tasks=tasks,test_url=test_url)
    else:
        tasks = get_tasks_from_redis(batch_id=batch_id,parent_id=parent_id)
        for t in tasks:
            t.task_id = str(t)
            t.state_track = get_status(batch_id=batch_id,parent_id=t.sub_id)
            for b in t.state_track:
                b.url = url_for("api_g5.get_tasks",batch_id=batch_id, parent_id=b.parent_id)
        return render_template("tasks.html", tasks=tasks,test_url=test_url)


@api_group5.route('/record_tasks', methods=['POST', "GET"])
def record_tasks():
    raw_data = request.values['msg']
    print(raw_data)
    data = json.loads(raw_data)
    new_obj = TaskTrackingRecord(**data)
    print(new_obj)
    sess = db.session()
    sess.add(new_obj)
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
    p=multiprocessing.Process(target=test_main,args=())
    p.start()
    msg = {"status": "success", "info": "测试任务已经启动"}
    return json.dumps(msg)