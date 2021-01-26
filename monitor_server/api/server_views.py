from flask import Blueprint, request,url_for,render_template
# from flask_restx import Api, Resource
# from monitor_server import app
from monitor_server import SoftPackage

api_group1 = Blueprint("api_g1",__name__)


@api_group1.route('/')
def overview():
    # return 'Hello World!'
    # print(url_for("api_g1.get_data", x=123,_external=True))
    print(request.method)
    return render_template("index.html",overview_class="active", pageheadershow=True, show_boards=True)


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


@api_group1.route('/containers', methods=['GET', 'POST'])
def get_containers():
    print(request.method)
    return render_template("containers.html", containers_class="active")



@api_group1.route('/products', methods=['GET', 'POST'])
def get_products():
    print(request.method)
    sps = SoftPackage.query.all()
    for sp in sps:
        print(sp)
    print(url_for("api_g1.add_products"))
    return render_template("products.html", products_class="active",
                           soft_packages=sps, url_for_add=url_for("api_g1.add_products"))

@api_group1.route('/products/add', methods=['GET', 'POST'])
def add_products():
    if request.method == "POST":
        print(request.form)
    return render_template("products_add.html", url_for_add=url_for("api_g1.add_products"))


# @api_group1.route('/data/<x>', methods=['GET'])
# def get_data(x):
#     print(request.method)
#     print(x)
#     return "yes"+x