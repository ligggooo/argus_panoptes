from flask import request,url_for,render_template
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from models import SoftPackage,db
from operation_utils.file import get_data_dir

from api import api_group1

_data_dir = get_data_dir()




@api_group1.route('/machines', methods=['GET', 'POST'])
def get_machines():
    print(request.method)
    if(request.method=="POST"):
        pass
    else:
        return render_template("machines.html", machines_class="active", show_boards=True,
                               url_for_add=url_for("api_group1.add_machines"))

@api_group1.route('/machines/add', methods=['GET', 'POST'])
def add_machines():
    return render_template("machines_add.html")










