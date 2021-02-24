from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db


class SoftPackage(db.Model):
    __tablename__ = "software_packages"
    __table_args__ = (
        UniqueConstraint("name", "main_version",
                         "second_version", "third_version","suffix"),
    )
    spid = db.Column(db.Integer, primary_key=True,autoincrement=True,name="id")
    package_name = db.Column(db.String(64), nullable=False,unique=False,name="name")
    main_version = db.Column(db.Integer, nullable=False)
    second_version = db.Column(db.Integer, nullable=False,default=0)
    third_version = db.Column(db.Integer, nullable=False,default=0)
    suffix = db.Column(db.String(8), default="")
    file_path = db.Column(db.String(256), nullable=False, unique=False)
    desc = db.Column(db.String(512), nullable=True, unique=False)
    reserve_1 = db.Column(db.String(256), nullable=True,unique=False)
    reserve_2 = db.Column(db.String(256), nullable=True,unique=False)
    def __repr__(self):
        return "<%s_v%d.%d.%d>" % (self.package_name,self.main_version,
                                   self.second_version,self.third_version)

    @property
    def full_name(self):
        return "%s_v%d.%d.%d.%s" % (self.package_name,self.main_version,
                                    self.second_version,self.third_version,self.suffix)

    @property
    def full_name_no_suffix(self):
        return "%s_v%d.%d.%d" % (self.package_name, self.main_version,
                                    self.second_version, self.third_version)

    @property
    def full_name_no_suffix_no_version(self):
        return "%s" % (self.package_name)


if __name__ == "__main__":
    db.create_all()
    for i in range(10):
        new_soft_pack = SoftPackage(package_name="dev_helloworld",
                                main_version=0,second_version=1,third_version=i,file_path="/mnt/data/software/0012",suffix="tar"
                                )
        if SoftPackage.query.filter_by(package_name=new_soft_pack.package_name,
                                       main_version=new_soft_pack.main_version,
                                       second_version=new_soft_pack.second_version,
                                       third_version=new_soft_pack.third_version).limit(1).all():
            print(new_soft_pack,"exists")
            continue
        sess = db.session()
        sess.add(new_soft_pack)
        sess.commit()
        sess.close()
        print(dir(new_soft_pack))
    print(SoftPackage.query.all())
