from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db


class Image(db.Model):
    __tablename__ = "images"
    __table_args__ = (
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_name = db.Column(db.String(32), nullable=False, unique=True)
    desc = db.Column(db.String(512), nullable=False, unique=False)
    size_in_MB = db.Column(db.Integer, nullable=False, unique=False)

    def __repr__(self):
        return "<%s>" % self.image_name


class Container(db.Model):
    __tablename__ = "containers"
    __table_args__ = (
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    container_name = db.Column(db.String(128), nullable=False, unique=True)
    command = db.Column(db.String(512), nullable=False, unique=True)
    image_id = db.Column(db.Integer, nullable=False, unique=False)
    machine_id = db.Column(db.Integer, nullable=False, unique=False)

    def __repr__(self):
        return "<%s %s>" % (self.ip_addr, self.host_name)

    @property
    def full_name(self):
        return "%s[ %s ]" % (self.ip_addr, self.host_name)



if __name__ == "__main__":
    db.create_all()
    sess = db.session()
    new_obj1 = Image(desc="demo ：支持ta sa", image_name="pytorch_gis_sa_ta_v202101.1", size_in_MB=321)
    new_obj2 = Image(desc="demo ：用于支撑集成服务", image_name="nginx_flask_jdk8_IA_v202101.1", size_in_MB=121)
    new_obj3 = Image(desc="demo ：支持GPU计算", image_name="GPU_v202101.1", size_in_MB=1422)
    #sess.add(new_obj1)
    sess.add(new_obj2)
    sess.add(new_obj3)
    sess.commit()