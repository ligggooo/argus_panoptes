from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db


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
        return "<%s %s>" % (self.ip_addr, self.host_name)

    @property
    def full_name(self):
        return "%s[ %s ]" % (self.ip_addr, self.host_name)

if __name__ == "__main__":
    db.create_all()