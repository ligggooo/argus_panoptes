from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db
from models.model_002_package import SoftPackage


class Deployment(db.Model):
    __tablename__ = "deployments"
    __table_args__ = (
        # UniqueConstraint("container_id","soft_package_id"), # 不可行，因为目前临时性上传的服务的package id被记为-11，是允许重复的。
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False, unique=False)
    desc = db.Column(db.String(256), nullable=False, unique=False)
    container_id = db.Column(db.Integer, nullable=False, unique=False)
    soft_package_id = db.Column(db.Integer, nullable=False, unique=False)

    def __repr__(self):
        return "<%s %s>" % (self.name, self.desc)

    @property
    def full_name(self):
        return "%s[ %s ]" % (self.ip_addr, self.host_name)

    @staticmethod
    def is_record_exist(container_id=container_id,soft_package_id=soft_package_id):
        sp = SoftPackage.query.filter_by(spid=soft_package_id).limit(2).all()
        if len(sp) == 0:
            return False, None
        else:
            records = Deployment.query.filter_by(container_id=container_id).join(SoftPackage,
                                                            SoftPackage.spid == Deployment.soft_package_id). \
                filter(SoftPackage.package_name == sp[0].package_name).all()
            if len(records) > 0:
                return True, records[0]
            else:
                return False, None


if __name__ == "__main__":
    # db.create_all()
    xx = Deployment.query.filter_by(container_id=1).join(SoftPackage, SoftPackage.spid==Deployment.soft_package_id).\
        filter(SoftPackage.package_name=="jiliang_monitor").all()
    for x in xx:
        print(x)