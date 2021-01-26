from flask import Blueprint, request,url_for,render_template
# from flask_restx import Api, Resource
# from monitor_server import app
from monitor_server import SoftPackage

api_group1 = Blueprint("api_g1",__name__)


@api_group1.route('/')
def hello_world():
    # return 'Hello World!'
    print(url_for("api_g1.get_data", x=123,_external=True))
    sps = SoftPackage.query.all()
    for sp in sps:
        print(sp)
    return render_template("index.html",soft_packages=sps, overview_class="active")

@api_group1.route('/machines', methods=['GET'])
def get_machines():
    print(request.method)
    return render_template("index.html", machines_class="active")


@api_group1.route('/data/<x>', methods=['GET'])
def get_data(x):
    print(request.method)
    print(x)
    return "yes"+x