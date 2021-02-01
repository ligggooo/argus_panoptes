from flask import Blueprint,request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from models import SoftPackage,db,Image,Machine,Container,Deployment
from operation_utils.dockers import get_docker_images

api_group3 = Blueprint("api_g3",__name__)

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

    members = Container.query
    if machine_id:
        members = members.filter_by(machine_id=machine_id)
    if image_id:
        members = members.filter_by(image_id=image_id)
    if (not machine_id) and (not image_id):
        members = members.all()

    url_for_add = url_for("api_g3.add_containers")
    url_for_search = url_for("api_g3.search_for_containers")
    for m in members:
        m.host_ip = Machine.query.filter_by(id=m.machine_id).all()[0].ip_addr
        m.image_name = Image.query.filter_by(id=m.image_id).all()[0].image_name
        #
        m.url_containers_on_image = url_for("api_g3.get_containers", image_id=m.image_id)
        m.url_containers_on_machine = url_for("api_g3.get_containers", machine_id=m.machine_id)
        m.edit_url = url_for("api_g3.edit_containers", num=m.id)
    return render_template("containers.html", containers_class="active", members=members,
                           url_for_add=url_for_add, url_for_search=url_for_search)


@api_group3.route('/containers/add', methods=['GET', 'POST'])
def add_containers():
    machines = Machine.query.all()
    machines = sorted(machines, key=lambda x:x.ip_addr)
    images = Image.query.all()
    # @todo
    return render_template("containers_add_edit.html",machines=machines, images=images, old_obj=None,host_ip_disabled="")


@api_group3.route('/containers/edit/<num>', methods=['GET', 'POST'])
def edit_containers(num):
    if request.method=="POST":
        data = request.form
        return '{"asadsa":123}'
    old_obj = Container.query.filter_by(id=num).all()[0]
    machines = Machine.query.all()
    machines = sorted(machines, key=lambda x:x.ip_addr)
    for m in machines:
        if m.id == old_obj.id:
            m.selected="selected"

    images = Image.query.all()
    for i in images:
        if i.id == old_obj.id:
            i.selected="selected"
    # @todo
    this_page = url_for("api_g3.edit_images", num=num)
    dest_page = url_for("api_g3.get_images")
    return render_template("containers_add_edit.html", machines=machines, images=images, old_obj=old_obj,
                           host_ip_disabled="disabled",this_page=this_page,dest_page=dest_page)


@api_group3.route('/containers/search', methods=['GET', 'POST'])
def search_for_containers():
    pass


@api_group3.route('/deployments', methods=['GET', 'POST'])
def get_deployments():
    print(request.method)
    members = Deployment.query.all()
    for m in members:
        m.container_name = Container.query.filter_by(id=m.container_id).all()[0].container_name
        m.package_name = SoftPackage.query.filter_by(spid=m.soft_package_id).all()[0].full_name
    return render_template("deployments.html", deployment_class="active",members=members)


@api_group3.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    return "todo"


