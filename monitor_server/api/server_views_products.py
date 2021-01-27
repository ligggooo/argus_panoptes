from flask import Blueprint,request, url_for, render_template, redirect, send_from_directory
import os
import json
from api.api_utils.clear_package import clear_package_name, clear_package_path
from models import SoftPackage, db

from operation_utils.file import get_data_dir

_data_dir = get_data_dir()
api_group1 = Blueprint("api_g1",__name__)

@api_group1.route('/')
def overview():
    # return 'Hello World!'
    # print(url_for("api_g1.get_data", x=123,_external=True))
    print(request.method)
    return render_template("index.html",overview_class="active", pageheadershow=True, show_boards=True)


@api_group1.route('/products', methods=['GET', 'POST'])
def get_products():
    print(request.method)
    sps = SoftPackage.query.all()
    for sp in sps:
        print(sp.package_name, sp.file_path)
        real_path = os.path.join(_data_dir +os.path.sep +sp.file_path,sp.full_name)
        sp.edit_url = url_for("api_g1.edit_products", num=sp.spid)
        sp.upload_url = url_for("api_g1.upload_products",num=sp.spid)
        sp.download_url = url_for("api_g1.download_products", num=sp.spid)
        sp.download_disabled = ""
        if os.path.exists(real_path):
            sp.desc = sp.desc
            sp.tr_class = "info"
        else:
            sp.desc = "文件不存在"
            sp.tr_class = "danger"
            sp.download_disabled="disabled"
    print(url_for("api_g1.add_products"))
    rm_post_url = url_for("api_g1.rm_products")
    return render_template("products.html", products_class="active",
                           soft_packages=sps, url_for_add=url_for("api_g1.add_products"),
                           url_for_rm_post=rm_post_url)


@api_group1.route('/products/add', methods=['GET', 'POST'])
def add_products():
    if request.method == "POST":
        full_name_splits,info_1 = clear_package_name(request.form["package_name"])
        package_path,info_2 = clear_package_path(request.form["package_path"])
        msg = {"status":"success", "info":"","info_1":info_1, "info_2":info_2}
        if full_name_splits and package_path:
            package_name, main_version, second_version, third_version, suffix = full_name_splits
            new_soft_pack = SoftPackage(package_name=package_name,
                                        main_version=main_version, second_version=second_version, third_version=third_version,
                                        suffix=suffix, file_path=package_path,
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
                msg["info"] = "record %s exists" % new_soft_pack
        else:
            msg['status'] = "fail"
            msg["info"] = "failed on clear"
        return json.dumps(msg)
    this_page = url_for("api_g1.add_products")
    dest_page = url_for("api_g1.get_products")
    rm_post_url = url_for("api_g1.rm_products")
    return render_template("products_add_edit.html", url_for_post=this_page,
                           success_url=dest_page,old_sp=None,
                           url_for_rm_post=rm_post_url,
                           )


@api_group1.route('/products/remove', methods=['POST'])
def rm_products():
    num = int(request.form.get("remove"))
    sess = db.session()
    sess.query(SoftPackage).filter(SoftPackage.spid == num).delete()
    sess.commit()
    msg = {"status": "success","target_url":url_for("api_g1.get_products")}
    return json.dumps(msg)


@api_group1.route('/products/edit/<num>', methods=['GET','POST'])
def edit_products(num):
    sess = db.session()

    if request.method == "POST":
        full_name_splits, info_1 = clear_package_name(request.form["package_name"])
        package_path, info_2 = clear_package_path(request.form["package_path"])
        desc = request.form["package_desc"]
        msg = {"status": "success", "info": "", "info_1": info_1, "info_2": info_2}
        if full_name_splits and package_path:
            package_name, main_version, second_version, third_version, suffix = full_name_splits

            if not SoftPackage.query.filter(SoftPackage.package_name==package_name,
                                               SoftPackage.main_version==main_version,
                                               SoftPackage.second_version==second_version,
                                               SoftPackage.third_version==third_version,
                                            SoftPackage.suffix==suffix,
                                            SoftPackage.spid!=num).limit(1).all():

                sess.query(SoftPackage).filter(SoftPackage.spid == num).update({
                    "package_name":package_name,
                    "main_version" : main_version,
                    "second_version" : second_version,
                    "third_version" : third_version,
                    "suffix":suffix,
                    "file_path":package_path,
                    "desc":desc
                })
                sess.commit()
            else:
                print(request.form["package_name"], "exists")
                msg['status'] = "fail"
                msg["info"] = "record %s exists" % request.form["package_name"]
        else:
            msg['status'] = "fail"
            msg["info"] = "failed on clear"
        return json.dumps(msg)
    this_page = url_for("api_g1.edit_products", num=num)
    dest_page = url_for("api_g1.get_products")
    old_sp = sess.query(SoftPackage).filter(SoftPackage.spid == num).all()[0]
    return render_template("products_add_edit.html", url_for_post=this_page, success_url=dest_page,old_sp=old_sp)


@api_group1.route('/products/upload/<num>', methods=['GET', 'POST'])
def upload_products(num):
    sp = SoftPackage.query.filter_by(spid=int(num)).all()[0]
    if request.method == 'POST':
        f = request.files['file']
        os.makedirs(os.path.join(_data_dir + os.path.sep + sp.file_path))
        upload_path = os.path.join(_data_dir + os.path.sep + sp.file_path, sp.full_name)
        f.save(upload_path)
        return redirect(url_for('api_g1.get_products'))
    return render_template('file_upload.html')


@api_group1.route('/products/download/<num>', methods=['GET'])
def download_products(num):
    sp = SoftPackage.query.filter_by(spid=int(num)).all()[0]
    download_path = os.path.join(_data_dir + os.path.sep + sp.file_path)
    filename = sp.full_name
    return send_from_directory(download_path,filename=filename,as_attachment=True)