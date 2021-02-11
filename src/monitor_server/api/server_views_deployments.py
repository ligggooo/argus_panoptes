from flask import Blueprint,request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from models import SoftPackage,db,Image,Machine,Container,Deployment
from operation_utils.dockers import get_docker_images, create_container, get_container, rm_container, start_container, \
    stop_container, restart_container, remove_container, cp_file_2_container
from operation_utils.file import get_tmp_data_dir,get_data_dir
__tmp_dir = get_tmp_data_dir()
__data_dir = get_data_dir()

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
        if m.soft_package_id==-11:
            m.package_name = "临时上传的文件"
            m.tr_class = "warning"
        else:
            packages = SoftPackage.query.filter_by(spid=m.soft_package_id).limit(2).all()
            if packages:
                m.package_name = packages[0].full_name
            else:
                m.package_name = "错误，找不到此软件版本"
                m.tr_class = "danger"
    return render_template("deployments.html", deployment_class="active",members=members,
                           url_for_add=url_for("api_g4.add_deployments"), url_for_rm_post=
                           url_for("api_g4.rm_deployments"))


@api_group4.route('/deployments/add', methods=['GET', 'POST'])
def add_deployments():
    this_page = url_for("api_g4.add_deployments")
    dest_page = url_for("api_g4.get_deployments")

    if request.method=="POST":
        msg = {"status": "success", "info": "ok", "target_url": dest_page}
        data = request.form
        file = request.files.get("file")
        soft_package_id = data.get("soft_package_id")
        container_id = data.get("container_id")
        service_name = data.get("service_name")
        service_desc = data.get("service_desc")

        if data.get("src_method") == "upload":
            file_path =os.path.join(__tmp_dir,file.filename)
            file.save(file_path)
            soft_package_id=-11  # 出于调试目的，临时上传的包被记为 -11#  允许重复
        elif data.get("src_method") == "select":
            sp = SoftPackage.query.filter_by(spid=soft_package_id).limit(2).all()[0]
            file_path = os.path.join(__data_dir+os.path.sep+sp.file_path,sp.full_name)
        else:
            return json.dumps({"status": "failed", "info": "只能上传或者选择文件"})
        container = Container.query.filter_by(id=container_id).all()[0]
        machine = Machine.query.filter_by(id=container.machine_id).all()[0]
        msg["status"], msg["info"] = cp_file_2_container(machine.ip_addr, machine.docker_server_port,
                                                         container.container_raw_id, file_path)
        if msg["info"] is not None:
            return json.dumps(msg)
        record_may_exist = Deployment.query.filter_by(container_id=container_id,soft_package_id=soft_package_id).limit(1).all()
        record_does_not_exists = (len(record_may_exist)==0)
        # 非调试目的，通过选择而部署的服务不允许存在多个拷贝
        if soft_package_id==-11 or (int(soft_package_id)>0 and record_does_not_exists):
            new_service = Deployment(name=service_name,desc=service_desc,container_id=container_id,soft_package_id=soft_package_id)
            db.session.add(new_service)
            db.session.commit()
        else: # 若存在则不新增记录，而是通知用户，旧服务被覆盖了
            msg["status"] = "warning"
            msg["info"] = "旧的服务已被覆盖"

        return json.dumps(msg)
    containers = Container.query.order_by("machine_id","container_name").all()
    for c in containers:
        machine = Machine.query.filter_by(id=c.machine_id).all()[0]
        c.host_ip = machine.ip_addr
    packages = SoftPackage.query.all()
    # url_for_upload = url_for("")
    return render_template("deployments_add_edit.html",containers=containers,soft_packages=packages, url_for_post=this_page, success_url=dest_page,old_obj=None)


@api_group4.route('/deployments/upload', methods=['GET', 'POST'])
def upload_deployments():
    pass


@api_group4.route('/deployments/remove', methods=['POST'])
def rm_deployments():
    num = int(request.form.get("remove"))
    sess = db.session()
    sess.query(Deployment).filter(Deployment.id == num).delete()
    sess.commit()
    # todo
    # 容器清理逻辑，需要每个服务包配置一个install一个uninstall脚本
    msg = {"status": "success","target_url":url_for("api_g4.get_deployments")}
    return json.dumps(msg)

