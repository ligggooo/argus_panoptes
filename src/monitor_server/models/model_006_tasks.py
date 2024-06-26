from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from monitor_server import db
from jiliang_process.process_monitor import CallCategory,StatePoint
from jiliang_process.status_track import StatusRecord


class TaskTrackingRecord(db.Model):
    __tablename__ = "task_track"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sub_id = db.Column(db.String(128), nullable=False, unique=False)
    parent_id = db.Column(db.String(128), nullable=True, unique=False)
    root_id = db.Column(db.String(128), nullable=False, unique=False)
    name = db.Column(db.String(128), nullable=False, unique=False)
    call_category = db.Column(db.Integer, nullable=False, unique=False)
    state = db.Column(db.Integer, nullable=False, unique=False)
    timestamp = db.Column(db.Float, nullable=False, unique=False)
    desc = db.Column(db.String(1024), nullable=True, unique=False)
    location = db.Column(db.String(256), nullable=True, default="unknown,unknown")

    def __repr__(self):
        return "<%s:%s %s:%s %s>" % (self.parent_id, self.sub_id, CallCategory(self.call_category).name, self.name, StatePoint(self.state).name)

    @property
    def full_name(self):
        return ""

    @staticmethod
    def is_record_exist():
        pass

    def freeze(self, safe=True)-> StatusRecord:
        """
        :return:
        """
        if safe:
            db.session.refresh(self)
        record = StatusRecord()
        record.sub_id = self.sub_id
        record.root_id = self.root_id
        record.parent_id = self.parent_id
        record.desc = self.desc
        record.state = self.state
        record.name = self.name
        record.call_category = self.call_category
        record.timestamp = self.timestamp
        record.location = self.location
        return record


class Task(db.Model):
    __tablename__ = "task"
    # __table_args__ = {"extend_existing":True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    root_id = db.Column(db.String(128), nullable=False, unique=False)
    root_tag = db.Column(db.String(128), nullable=False, unique=False)
    name = db.Column(db.String(128), nullable=False, unique=False, default="测试")
    start_time = db.Column(db.Float, nullable=False, unique=False, default=-1)
    end_time = db.Column(db.Float, nullable=False, unique=False, default=-1)
    desc = db.Column(db.String(1024), nullable=True, unique=False)

    def __repr__(self):
        return "%s <%s:%s>"%(self.name, self.root_tag,self.root_id)


def create_all():
    db.create_all()

if __name__ == "__main__":
    db.create_all()
