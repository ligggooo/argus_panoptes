from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint

from monitor_server import db


class Users1(db.Model):
    __tablename__ = "users"
    id  = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),nullable=False,unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    def __repr__(self):
        return "<Users %r>" %self.username

class ProcessState(db.Model):
    __tablename__ = "process_state"
    __table_args__ = (
        PrimaryKeyConstraint("batch_id","tile_id","task_id","stage_id", name="pkey"),
    )
    batch_id = db.Column(db.String(255),nullable=False)
    old_batch_id = db.Column(db.String(255),nullable=True)
    hsd_time_start = db.Column(db.TIMESTAMP(6),nullable=True)
    hsd_time_end = db.Column(db.TIMESTAMP(6), nullable=True)
    hsd_source = db.Column(db.String(255), nullable=True)
    task_id = db.Column(db.String(10), nullable=False)
    total_task_cnt = db.Column(db.Integer, nullable=True)
    stage_id =db.Column(db.String(255),nullable=False)
    tile_id = db.Column(db.String(255),nullable=False)
    status =db.Column(db.String(255),nullable=False)
    vid = db.Column(db.String(255),nullable=True)

    def __repr__(self):
        return self.batch_id






if __name__ == "__main__":
    # create_all()
    user = ProcessState.query.all()
    print(user)