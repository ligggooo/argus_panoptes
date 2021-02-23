from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db
from jiliang_process.process_monitor import CallCategory,StatePoint


class TaskTrackingRecord(db.Model):
    __tablename__ = "task_track"
    __table_args__ = ()
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sub_id = db.Column(db.String(128), nullable=False, unique=False)
    parent_id = db.Column(db.String(128), nullable=True, unique=False)
    name = db.Column(db.String(128), nullable=False, unique=False)
    call_category = db.Column(db.Integer, nullable=False, unique=False)
    state = db.Column(db.Integer, nullable=False, unique=False)
    timestamp = db.Column(db.Float, nullable=False, unique=False)
    index = db.Column(db.Integer, nullable=False, unique=False, default=0)
    desc = db.Column(db.String(1024), nullable=True, unique=False)

    def __repr__(self):
        return "<%s:%s %s:%s %s>" % (self.parent_id, self.sub_id, CallCategory(self.call_category).name, self.name, StatePoint(self.state).name)

    @property
    def full_name(self):
        return ""

    @staticmethod
    def is_record_exist():
        pass


class Task(db.Model):
    __tablename__ = "task"
    __table_args__ = ()
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String(128), nullable=False, unique=False)
    desc = db.Column(db.String(256), nullable=False, unique=False)

if __name__ == "__main__":
    db.create_all()
