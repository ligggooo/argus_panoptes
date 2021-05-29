from flask import Blueprint, request, url_for, render_template
import os
import json

from typing import List

from flask_cors import cross_origin

from monitor_server.models.model_002_package import SoftPackage, db
from monitor_server.models.model_003_machines import Machine, PhysicalPort
from operation_utils.file import get_data_dir

_data_dir = get_data_dir()
api_group2 = Blueprint("api_g2", __name__)


@api_group2.route('/machines', methods=['GET'])
def get_machines():
    machines = Machine.query.all()
    machines = sorted(machines, key=lambda x: x.ip_addr)
    for m in machines:
        print(m)
        m.url_containers = url_for("api_g3.get_containers", machine_id=m.id)
        print(m.url_containers)
        m.ports = PhysicalPort.query.filter_by(machine_id=m.id).all()
        if len(m.ports) > 0:
            m.port_btn_class = "btn-info"
        for p in m.ports:
            if p.available == 1:
                p.li_class = "info"
            else:
                p.li_class = "disabled"
                p.info = "被占用"
    return render_template("machines.html", machines_class="active", show_boards=True,
                           url_for_add=url_for("api_g2.add_machines"), machines=machines)


@api_group2.route('/get_machines/', methods=['GET'])
@cross_origin()
def get_machines_v2():
    machines:List[Machine] = Machine.query.all()
    machines = sorted(machines, key=lambda x: x.ip_addr)
    for m in machines:
        print(m)
        m.url_containers = url_for("api_g3.get_containers", machine_id=m.id)
        print(m.url_containers)
        m.ports:List[PhysicalPort] = PhysicalPort.query.filter_by(machine_id=m.id).all()
        if len(m.ports) > 0:
            m.port_btn_class = "btn-info"
        for p in m.ports:
            if p.available == 1:
                p.li_class = "info"
            else:
                p.li_class = "disabled"
                p.info = "被占用"

    items = [{
        "id":m.id,
        "ip":m.ip_addr,
        "hostname":m.host_name,
        "cpu":m.cpu_cores,
        "free_memory":m.free_mem_in_MB,
        "open_port":[{"portnum":p.port_num,"free":str(p.available) }for p in m.ports],
        "deploy_point_one": m.deploy_point_1,
        "deploy_one_free_memory": m.free_storage_in_GB_1,
        "deploy_point_two": m.deploy_point_2,
        "deploy_two_free_memory": m.free_storage_in_GB_2,
        "docker_sever_port": m.docker_server_port
    }
        for m in machines
    ]
    ret = {
        "code":200,
        "message" : "success",
        "data":{
            "count":len(machines),
            "data":items
        }
    }
    return json.dumps(ret)

@api_group2.route('/add_machines', methods=['GET'])
def add_machines():
    return "todo"


@api_group2.route('/machines_del/', methods=['DELETE'])
def del_machines():
    id = request.args.get("id", None)
    if id:
        sess = db.session()
        machines = sess.query(Machine).filter_by(id=id).limit(1).all()
        if len(machines) > 0:
            sess.delete(machines[0])
            sess.commit()
            ret = {
                "code": 200,
                "message": "success",
                "data": "删除成功"
            }
        else:
            ret = {
                "code": 503,
                "message": "failed",
                "data": "不存在此机器"
            }
        sess.close()

    else:
        ret = {
            "code": 503,
            "message": "failed",
            "data": "不存在此机器"
        }
    return json.dumps(ret)


@api_group2.route('/machines_set/', methods=['GET'])
@cross_origin()
def set_machines():
    name = request.args.get("name", None)
    info = request.args.get("info", None)
    id = request.args.get("id", None)
    ret = {
        "code": 200,
        "message": "success",
        "data": "设置成功"
        }
    return json.dumps(ret)