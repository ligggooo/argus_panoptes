from flask import Blueprint, request,url_for,render_template
import json
# from flask_restx import Api, Resource
# from monitor_server import app
from api.api_utils.clear_package import clear_package_name, clear_package_path
from monitor_server import SoftPackage,db

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
        full_name_splits,info_1 = clear_package_name(request.form["package_name"])
        package_path,info_2 = clear_package_path(request.form["package_path"])
        msg = {"status":"success", "info":"","info_1":info_1, "info_2":info_2}
        if full_name_splits and package_path:
            package_name, main_version, second_version, third_version = full_name_splits
            new_soft_pack = SoftPackage(package_name=package_name,
                                        main_version=main_version, second_version=second_version, third_version=third_version,
                                        file_path=package_path,
                                        )
            if not SoftPackage.query.filter_by(package_name=new_soft_pack.package_name,
                                           main_version=new_soft_pack.main_version,
                                           second_version=new_soft_pack.second_version,
                                           third_version=new_soft_pack.third_version).limit(1).all():
                sess = db.session()
                sess.add(new_soft_pack)
                sess.commit()
            else:
                print(new_soft_pack, "exists")
                msg['status'] = "fail"
                msg["info"] = "%s exists" % new_soft_pack
        else:
            msg['status'] = "fail"
            msg["info"] = "failed on clear"
        return json.dumps(msg)
    this_page = url_for("api_g1.add_products")
    dest_page = url_for("api_g1.get_products")
    return render_template("products_add.html", url_for_add=this_page, success_url=dest_page)


# @api_group1.route('/data/<x>', methods=['GET'])
# def get_data(x):
#     print(request.method)
#     print(x)
#     return "yes"+x