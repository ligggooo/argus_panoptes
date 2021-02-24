from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint

from api.api_utils.portmapping_parser import port_mapping_str2list
from monitor_server import db
from models.model_003_machines import PhysicalPort

db.metadata.clear()
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
    container_raw_id = db.Column(db.String(128), nullable=False, unique=False)
    container_name = db.Column(db.String(128), nullable=False, unique=False)
    command = db.Column(db.String(512), nullable=False, unique=False)
    image_id = db.Column(db.Integer, nullable=False, unique=False)
    machine_id = db.Column(db.Integer, nullable=False, unique=False)
    port_mapping = db.Column(db.String(128), nullable=True, unique=False)

    def __repr__(self):
        return "<%s %s>" % (self.machine_id, self.container_name)

    @property
    def full_name(self):
        return "%s[ %s ]" % (self.ip_addr, self.host_name)

    @staticmethod
    def remove(container):
        db.session.delete(container)
        port_mapping_to_release, _ = port_mapping_str2list(container.port_mapping)
        ports_to_release = [pp.to_port for pp in port_mapping_to_release]
        ports_obj_to_release = PhysicalPort.query.filter(PhysicalPort.machine_id == container.machine_id,
                                                         PhysicalPort.port_num.in_(ports_to_release)).all()
        for x in ports_obj_to_release:
            x.available = 1
        db.session.commit()

    @staticmethod
    def add(container):
        db.session.add(container)
        port_mapping_to_possess, _ = port_mapping_str2list(container.port_mapping)
        ports_to_possess= [pp.to_port for pp in port_mapping_to_possess]
        ports_obj_to_release = PhysicalPort.query.filter(PhysicalPort.machine_id == container.machine_id,
                                                         PhysicalPort.port_num.in_(ports_to_possess)).all()
        for x in ports_obj_to_release:
            x.available = 0
        db.session.commit()


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