from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db


class Deployment(db.Model):
    __tablename__ = "deployments"
    __table_args__ = ( )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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