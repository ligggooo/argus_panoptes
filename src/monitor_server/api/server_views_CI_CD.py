from flask import Blueprint,request,url_for,render_template
import os
import json
from monitor_server.api.api_utils.clear_package import clear_package_name, clear_package_path

from operation_utils.dockers import get_docker_images, create_container, get_container, rm_container, start_container, \
    stop_container, restart_container, remove_container

api_group6 = Blueprint("api_g6",__name__)


@api_group6.route('/webhook', methods=['GET', 'POST'])
def webhook():
    print("自动测试和自动部署")
    return "正在设计任务监控方案"


