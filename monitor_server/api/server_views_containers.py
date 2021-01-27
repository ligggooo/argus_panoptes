from flask import request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from models import SoftPackage,db
from api import api_group1



@api_group1.route('/containers', methods=['GET', 'POST'])
def get_containers():
    print(request.method)
    return render_template("containers.html", containers_class="active")



