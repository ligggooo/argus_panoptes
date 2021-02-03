from flask import Blueprint,request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from models import SoftPackage,db,Image,Machine,Container,Deployment
from operation_utils.dockers import get_docker_images, create_container, get_container, rm_container, start_container, \
    stop_container, restart_container, remove_container

api_group5 = Blueprint("api_g5",__name__)




@api_group5.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    return "todo"


