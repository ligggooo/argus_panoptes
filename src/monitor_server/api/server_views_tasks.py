from flask import Blueprint,request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from api.api_utils.task_analysis import get_status
from models import SoftPackage,db,Image,Machine,Container,Deployment,TaskTrack,Task
from operation_utils.dockers import get_docker_images, create_container, get_container, rm_container, start_container, \
    stop_container, restart_container, remove_container

api_group5 = Blueprint("api_g5",__name__)


# 定时任务周期性地读取数据库,将分析结果读入redis
# get_task 从redis中读取分析结果，呈现到前端

@api_group5.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    from jiliang_process.graph_test import state_graph
    tasks = Task.query.all()

    for t in tasks:
        t.state_track = get_status(tag="root")
    return render_template("tasks.html", tasks=tasks)


@api_group5.route('/record_tasks', methods=['POST', "GET"])
def record_tasks():
    raw_data = request.values['msg']
    print(raw_data)
    data = json.loads(raw_data)
    new_obj = TaskTrack(**data)
    print(new_obj)
    sess = db.session()
    sess.add(new_obj)
    sess.commit()
    return "ok"
