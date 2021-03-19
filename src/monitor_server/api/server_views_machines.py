from flask import Blueprint, request, url_for, render_template
import os
import json
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


@api_group2.route('/machines/add', methods=['GET', 'POST'])
def add_machines():
    return render_template("machines_add.html")
