from flask import Blueprint,request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from api.api_utils.portmapping_parser import port_mapping_str2list, check_ports, port_mapping_list2dict, update_ports, \
    port_mapping_str2dict
from models import SoftPackage,db,Image,Machine,Container,Deployment,PhysicalPort
from operation_utils.dockers import get_docker_images, create_container, get_container, rm_container, start_container, \
    stop_container, restart_container, remove_container, cp_file_from_container, write_content_2_container
from operation_utils.file import get_tmp_data_dir


api_group3 = Blueprint("api_g3",__name__)

_tmp_data_dir = get_tmp_data_dir()


@api_group3.route('/images', methods=['GET', 'POST'])
def get_images():
    print(request.method)
    members = Image.query.all()
    images = get_docker_images()
    for m in members:
        m.tr_class = "info"
        if m.image_name in images:
            m.size_in_MB = images[m.image_name].size_in_mb
            images.pop(m.image_name)
        else:
            m.info = "找不到此镜像"
            m.tr_class = "danger"
    sess = db.session()
    for n in images:
        new_obj1 = Image(desc="[ None ]", image_name=n, size_in_MB=images[n].size_in_mb)
        sess.add(new_obj1)
        new_obj1.tr_class = "info"
        members.append(new_obj1)
    sess.commit()
    for m in members:
        m.edit_url = url_for("api_g3.edit_images", num=m.id)
        m.url_containers = url_for("api_g3.get_containers", image_id=m.id)
    return render_template("images.html", images_class="active",members=members)


@api_group3.route('/images/edit/<num>', methods=['GET', 'POST'])
def edit_images(num):
    print(request.method)
    old_obj = db.session.query(Image).filter(Image.id == num).all()[0]
    if request.method == "POST":
        msg = {"status":"success"}
        content = request.form
        old_obj.image_name = content.get("image_name")
        old_obj.desc = content.get("package_desc")
        db.session.commit()
        return json.dumps(msg)
    this_page = url_for("api_g3.edit_images", num=num)
    dest_page = url_for("api_g3.get_images")

    return render_template("images_add_edit.html", url_for_post=this_page, success_url=dest_page, old_obj=old_obj)


@api_group3.route('/containers', methods=['GET', 'POST'])
def get_containers():
    print(request.method)
    machine_id = request.args.get("machine_id")
    image_id = request.args.get("image_id")
    container_id = request.args.get("container_id")

    members = Container.query
    if machine_id:
        members = members.filter_by(machine_id=machine_id)
    if image_id:
        members = members.filter_by(image_id=image_id)
    if container_id:
        members = members.filter_by(id=container_id)

    members = members.all()

    url_for_add = url_for("api_g3.add_containers")
    url_for_search = url_for("api_g3.search_for_containers")
    for m in members:
        machine = Machine.query.filter_by(id=m.machine_id).all()[0]
        m.host_ip = machine.ip_addr
        m.image_name = Image.query.filter_by(id=m.image_id).all()[0].image_name

        c, err_msg = get_container(machine.ip_addr,machine.docker_server_port, m.container_raw_id)
        m.detail = err_msg.replace("\n","<br>")
        if not c:
            m.status = "error"
            m.tr_class = "danger"
        else:
            m.status = c.status
            if(c.status) =="running":
                m.tr_class = "success"
        #
        m.url_check_services = url_for("api_g4.get_deployments", container_id=m.id)
        m.services = Deployment.query.filter_by(container_id=m.id).all()
        m.port_mappings,msg = port_mapping_str2list(m.port_mapping)
        m.url_containers_on_image = url_for("api_g3.get_containers", image_id=m.image_id)
        m.url_containers_on_machine = url_for("api_g3.get_containers", machine_id=m.machine_id)
        m.edit_url = url_for("api_g3.edit_containers", num=m.id)
        m.start_url = url_for("api_g3.activate_containers", num=m.id, action="start")
        m.stop_url = url_for("api_g3.activate_containers", num=m.id, action="stop")
        m.restart_url = url_for("api_g3.activate_containers", num=m.id, action="restart")
        m.remove_url = url_for("api_g3.activate_containers", num=m.id, action="remove")
        m.edit_startup_url = url_for("api_g3.edit_startup_script", num=m.id, action="remove")
    return render_template("containers.html", containers_class="active", members=members,
                           url_for_add=url_for_add, url_for_search=url_for_search,url_base=url_for("api_g3.get_containers"))


@api_group3.route('/containers/action/<num>/<action>', methods=['POST'])
def activate_containers(num,action):
    target_url = url_for("api_g3.get_containers")
    msg = {"status": "success", "info": num + " " + action, "target_url": target_url}
    container = Container.query.filter_by(id=num).all()[0]
    machine = Machine.query.filter_by(id=container.machine_id).all()[0]
    if action=="start":
        msg["status"], msg["info"] = start_container(machine.ip_addr,machine.docker_server_port,container.container_raw_id)
    elif action=="stop":
        msg["status"], msg["info"] = stop_container(machine.ip_addr,machine.docker_server_port,container.container_raw_id)
    elif action=="restart":
        msg["status"], msg["info"] = restart_container(machine.ip_addr,machine.docker_server_port,container.container_raw_id)
    elif action == "remove":
        msg["status"], msg["info"] = remove_container(machine.ip_addr, machine.docker_server_port,
                                                       container.container_raw_id)
        Container.remove(container)
    return json.dumps(msg)


@api_group3.route('/containers/add', methods=['GET', 'POST'])
def add_containers():
    if request.method=="POST":
        msg = {"status":"success","info":"ok"}
        print(request.form)
        container_name = request.form.get("container_name")
        command = request.form.get("command")
        machine_id = request.form.get("machine_id")
        port_mapping_raw = request.form.get("port_mapping")
        port_mapping,err_msg = port_mapping_str2list(port_mapping_raw)
        if port_mapping==-1:
            msg["info"] = "端口映射填写错误："+err_msg
            msg['status'] = "failed"
            return json.dumps(msg)
        image_id = request.form.get("image_id")
        machine = Machine.query.filter_by(id=machine_id).all()[0]
        available_port_objs = PhysicalPort.query.filter(PhysicalPort.machine_id == machine.id,
                                                    PhysicalPort.available == 1).all()
        ret, err_msg = check_ports(available_port_objs, port_mapping)
        if ret==-1:
            msg["info"] = "端口映射填写错误：" + err_msg
            msg['status'] = "failed"
            return json.dumps(msg)

        port_mapping_dict =port_mapping_list2dict(port_mapping)
        image = Image.query.filter_by(id=image_id).all()[0]
        c,err_msg = create_container(machine.ip_addr, machine.docker_server_port, image.image_name, container_name,
                                     command, port_mapping=port_mapping_dict)
        if not c:
            msg["info"] = err_msg
            msg['status'] = "failed"
        else:
            Container.add(Container(container_name=container_name,container_raw_id=c.id,machine_id=machine_id,
                                     image_id=image_id,command=command,port_mapping=port_mapping_raw))
        return json.dumps(msg)
    machines = Machine.query.all()
    machines = sorted(machines, key=lambda x: x.ip_addr)
    images = Image.query.all()
    this_page = url_for("api_g3.add_containers")
    dest_page = url_for("api_g3.get_containers")
    return render_template("containers_add_edit.html", machines=machines, images=images,
                           old_obj=None, port_mapping_placeholder="60020,60030",
                           host_ip_disabled="", url_for_post=this_page, success_url=dest_page)


@api_group3.route('/containers/edit/<num>', methods=['GET', 'POST'])
def edit_containers(num):
    old_obj = Container.query.filter_by(id=num).all()[0]
    if request.method=="POST":
        msg = {"status": "success", "info": "ok"}
        print(request.form)
        container_name = request.form.get("container_name")
        command = request.form.get("command")
        machine_id = request.form.get("machine_id")
        image_id = request.form.get("image_id")
        machine = Machine.query.filter_by(id=machine_id).all()[0]
        image = Image.query.filter_by(id=image_id).all()[0]
        # todo  旧容器删除
        if int(old_obj.image_id) == int(image_id):
            old_obj.command = command
            old_obj.container_name = container_name
        else:
            rm_container(machine.ip_addr, machine.docker_server_port, old_obj.container_raw_id)
            port_mapping_str = old_obj.port_mapping
            port_mapping_dict = port_mapping_str2dict(port_mapping_str)
            c, err_msg = create_container(machine.ip_addr, machine.docker_server_port, image.image_name, container_name,
                                          command,port_mapping=port_mapping_dict)
            if not c:
                msg["info"] = err_msg
                msg['status'] = "failed"
            else:
                Container.remove(old_obj)
                Container.add(
                    Container(container_name=container_name, container_raw_id=c.id, machine_id=machine_id, image_id=image_id,
                              command=command,port_mapping=port_mapping_str))
        db.session.commit()
        return json.dumps(msg)

    machines = Machine.query.all()
    machines = sorted(machines, key=lambda x:x.ip_addr)
    for m in machines:
        if m.id == old_obj.machine_id:
            m.selected="selected"

    images = Image.query.all()
    for i in images:
        if i.id == old_obj.image_id:
            i.selected="selected"

    this_page = url_for("api_g3.edit_containers", num=num)
    dest_page = url_for("api_g3.get_containers")
    return render_template("containers_add_edit.html", machines=machines, images=images, old_obj=old_obj,
                           host_ip_disabled="disabled",command_ip_disabled="disabled", url_for_post=this_page,success_url=dest_page)


@api_group3.route('/containers/startup_edit/<num>', methods=['GET', 'POST'])
def edit_startup_script(num):
    container = Container.query.filter_by(id=num).all()[0]
    machine = Machine.query.filter_by(id=container.machine_id).all()[0]
    if request.method== "POST":
        msg = {"status": "success", "info": "ok"}
        content = request.form.get("startup_content")
        msg["status"], msg["info"]= write_content_2_container(machine.ip_addr, machine.docker_server_port, container.container_raw_id, content, file_path="/run.sh")
        return json.dumps(msg)
    status, info = cp_file_from_container(machine.ip_addr, machine.docker_server_port, container.container_raw_id, "/run.sh")
    if status == "success":
        tmp_dir,name = info
        content = open(os.path.join(tmp_dir,name)).read()
    else:
        content = "/bin/bash\n"
    this_page = url_for("api_g3.edit_startup_script", num=num)
    dest_page = url_for("api_g3.get_containers")
    return render_template("containers_startup_edit.html", content=content, url_for_post=this_page,success_url=dest_page)


@api_group3.route('/containers/search', methods=['GET', 'POST'])
def search_for_containers():
    pass




