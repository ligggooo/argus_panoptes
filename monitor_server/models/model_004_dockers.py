from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db


class Image(db.Model):
    __tablename__ = "images"
    __table_args__ = (
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_name = db.Column(db.String(32), nullable=False, unique=True)
    size_in_GB = db.Column(db.Integer, nullable=False, unique=False)


class Container(db.Model):
    __tablename__ = "containers"
    __table_args__ = (
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_name = db.Column(db.String(32), nullable=False, unique=True)
    image_id = db.Column(db.Integer, nullable=False, unique=False)
    machine_id = db.Column(db.Integer, nullable=False, unique=False)

    def __repr__(self):
        return "<%s %s>" % (self.ip_addr, self.host_name)

    @property
    def full_name(self):
        return "%s[ %s ]" % (self.ip_addr, self.host_name)



if __name__ == "__main__":
    db.create_all()