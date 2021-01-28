from flask import Blueprint,request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from models import SoftPackage,db,Image,Machine,Container,Deployment

api_group3 = Blueprint("api_g3",__name__)

@api_group3.route('/images', methods=['GET', 'POST'])
def get_images():
    print(request.method)
    members = Image.query.all()
    return render_template("images.html", images_class="active",members=members)

@api_group3.route('/containers', methods=['GET', 'POST'])
def get_containers():
    print(request.method)
    members = Container.query.all()
    for m in members:
        m.host_ip = Machine.query.filter_by(id=m.machine_id).all()[0].ip_addr
        m.image_name = Image.query.filter_by(id=m.image_id).all()[0].image_name
    return render_template("containers.html", containers_class="active",members=members)



@api_group3.route('/deployments', methods=['GET', 'POST'])
def get_deployments():
    print(request.method)
    members = Deployment.query.all()
    for m in members:
        m.container_name = Container.query.filter_by(id=m.container_id).all()[0].container_name
        m.package_name = SoftPackage.query.filter_by(spid=m.soft_package_id).all()[0].full_name
    return render_template("deployments.html", deployment_class="active",members=members)


@api_group3.route('/tasks', methods=['GET', 'POST'])
def get_taskss():
    return "todo"


