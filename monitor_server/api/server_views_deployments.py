from flask import Blueprint,request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from models import SoftPackage,db,Image,Machine,Container,Deployment
from operation_utils.dockers import get_docker_images, create_container, get_container, rm_container, start_container, \
    stop_container, restart_container, remove_container

api_group4 = Blueprint("api_g4" ,__name__)


@api_group4.route('/deployments', methods=['GET', 'POST'])
def get_deployments():
    print(request.method)
    container_id = request.args.get("container_id")
    package_id = request.args.get("package_id")

    members = Deployment.query
    if container_id:
        members = members.filter_by(container_id=container_id)
    if package_id:
        members = members.filter_by(soft_package_id=package_id)
    members = members.all()


    for m in members:
        containers = Container.query.filter_by(id=m.container_id).limit(2).all()
        m.url_deployments_in_container = url_for("api_g4.get_deployments",container_id=m.container_id)
        m.url_go_to_this_container = url_for("api_g3.get_containers",container_id=m.container_id)
        if containers:
            m.container_name = containers[0].container_name
        else:
            m.container_name = "错误，找不到此容器"
            m.tr_class = "danger"
        packages = SoftPackage.query.filter_by(spid=m.soft_package_id).limit(2).all()
        if packages:
            m.package_name = packages[0].full_name
        else:
            m.package_name = "错误，找不到此软件版本"
            m.tr_class = "danger"
    return render_template("deployments.html", deployment_class="active",members=members,url_for_add=url_for("api_g4.add_deployments"))

@api_group4.route('/deployments/add', methods=['GET', 'POST'])
def add_deployments():
    this_page = url_for("api_g4.add_deployments")
    dest_page = url_for("api_g4.get_deployments")
    containers = Container.query.order_by("machine_id","container_name").all()
    for c in containers:
        machine = Machine.query.filter_by(id=c.machine_id).all()[0]
        c.host_ip = machine.ip_addr
    packages = SoftPackage.query.all()
    return render_template("deployments_add_edit.html",containers=containers,soft_packages=packages, url_for_post=this_page, success_url=dest_page,old_obj=None)
#     if request.method=="POST":
#         msg = {"status":"success","info":"ok"}
#         print(request.form)
#         container_name = request.form.get("container_name")
#         command = request.form.get("command")
#         machine_id = request.form.get("machine_id")
#         image_id = request.form.get("image_id")
#         machine = Machine.query.filter_by(id=machine_id).all()[0]
#         image = Image.query.filter_by(id=image_id).all()[0]
#         c,err_msg = create_container(machine.ip_addr, machine.docker_server_port, image.image_name, container_name, command)
#         if not c:
#             msg["info"] = err_msg
#             msg['status'] = "failed"
#         else:
#             db.session.add(Container(container_name=container_name,container_raw_id=c.id,machine_id=machine_id,image_id=image_id,command=command))
#             db.session.commit()
#         return json.dumps(msg)
#     machines = Machine.query.all()
#     machines = sorted(machines, key=lambda x: x.ip_addr)
#     images = Image.query.all()
#     this_page = url_for("api_g3.add_containers")
#     dest_page = url_for("api_g3.get_containers")




