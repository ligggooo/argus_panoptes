from flask import Blueprint, request,url_for,render_template
# from flask_restx import Api, Resource
# from monitor_server import app
from monitor_server import SoftPackage

api_group1 = Blueprint("api_g1",__name__)


@api_group1.route('/')
def overview():
    # return 'Hello World!'
    print(url_for("api_g1.get_data", x=123,_external=True))
    return render_template("index.html",overview_class="active", pageheadershow=True, show_boards=True)

@api_group1.route('/machines', methods=['GET'])
def get_machines():
    print(request.method)
    return render_template("index.html", machines_class="active", show_boards=True)

@api_group1.route('/containers', methods=['GET'])
def get_containers():
    print(request.method)
    return render_template("index.html", containers_class="active")

@api_group1.route('/products', methods=['GET'])
def get_products():
    print(request.method)
    sps = SoftPackage.query.all()
    for sp in sps:
        print(sp)
    return render_template("index.html", products_class="active",soft_packages=sps)


@api_group1.route('/data/<x>', methods=['GET'])
def get_data(x):
    print(request.method)
    print(x)
    return "yes"+x