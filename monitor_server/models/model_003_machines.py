from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db


class Machine(db.Model):
    __tablename__ = "machines"
    __table_args__ = (
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_addr = db.Column(db.String(32), nullable=False, unique=True)
    host_name = db.Column(db.String(32), default="N/A", unique=False)
    cpu_cores = db.Column(db.Integer, nullable=False, unique=False)
    free_mem_in_MB = db.Column(db.Integer, nullable=False, unique=False)
    deploy_point_1 = db.Column(db.String(256), nullable=False, unique=False)
    free_storage_in_GB_1 = db.Column(db.Integer, nullable=False, unique=False)
    deploy_point_2 = db.Column(db.String(256), nullable=True, unique=False)
    free_storage_in_GB_2 = db.Column(db.Integer, nullable=True, unique=False)
    reserve_1 = db.Column(db.String(256), nullable=True, unique=False)
    reserve_2 = db.Column(db.String(256), nullable=True, unique=False)

    def __repr__(self):
        return "<%s %s>" % (self.ip_addr, self.host_name)

    @property
    def full_name(self):
        return "%s[ %s ]" % (self.ip_addr, self.host_name)


if __name__ == "__main__":

    for i in range(10):
        new_obj = Machine(ip_addr="10.130.160.11"+str(i),
                          host_name="hc-app-"+str(i), cpu_cores=16, free_mem_in_MB=304, deploy_point_1="/mnt/", free_storage_in_GB_1=1700
                          )
        if Machine.query.filter_by(ip_addr=new_obj.ip_addr).limit(1).all():
            print(new_obj, "exists")
            continue
        sess = db.session()
        sess.add(new_obj)
        sess.commit()
        print(dir(new_obj))
    print(Machine.query.all())