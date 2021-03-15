import logging
import queue
import threading
import time
from psycopg2.extras import execute_values

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import sessionmaker

engine = sqlalchemy.create_engine("postgresql://postgres:123456@10.130.160.114:60030/my_test")
# engine = sqlalchemy.create_engine("sqlite:///my_db.sqlite")

# con = engine.rawconnection()
cur = engine.raw_connection().cursor()
dbSession = sessionmaker(bind=engine)

Base = declarative_base()

class DataModel(Base):
    __tablename__ = "xxx_test"

    id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    package_name = Column(String(64), nullable=False, unique=False, default="name")


Base.metadata.create_all(bind=engine)

class DBWriter(threading.Thread):
    def __init__(self, session_factory, size=1000, batch_size=500, danger_level=800):
        threading.Thread.__init__(self)
        self.session_factory = session_factory
        # self.table = table
        self.queue = queue.Queue(size)
        self.batch_size = batch_size
        self.danger_level = danger_level

    def insert(self, obj):
        self.queue.put(obj)

    def run(self):
        cnt = 0
        while 1:
            if self.queue.qsize()>self.batch_size:
                if self.queue.qsize() > self.danger_level:
                    logging.warning("danger queue.qsize() exceeds danger_limit %d" % self.danger_level)
                # objs = []
                # for i in range(self.queue.qsize()):
                #     objs.append(self.queue.get())
                # sess = self.session_factory()
                # sess.add_all(objs)
                # sess.commit()
                # sess.close()
                xx = []
                for i in range(self.queue.qsize()):
                    xx.append([self.queue.get().package_name])
                # cur.executemany("INSERT INTO xxx_test (package_name) VALUES %s", xx)
                execute_values(cur, "INSERT INTO xxx_test (package_name) VALUES %s", xx)
                cur.connection.commit()
                cnt = 0
            if cnt > 10:
                # objs = []
                # for i in range(self.queue.qsize()):
                #     objs.append(self.queue.get())
                # sess = self.session_factory()
                # sess.bulk_save_objects(objs)
                # sess.commit()
                # sess.close()
                xx = []
                for i in range(self.queue.qsize()):
                    xx.append([self.queue.get().package_name])
                execute_values(cur, "INSERT INTO xxx_test (package_name) VALUES %s", xx)
                cnt = 0
            cnt += 1
            time.sleep(0.5)


dbw = DBWriter(dbSession)
dbw.start()

for i in range(10000):
    obj = DataModel(id=i+90000,package_name="obj-%d"%i)
    dbw.insert(obj)
    print(i,"====>", dbw.queue.qsize())
    time.sleep(0.001)
time.sleep(1)
print(i,"====>", dbw.queue.qsize())
dbw.join()


