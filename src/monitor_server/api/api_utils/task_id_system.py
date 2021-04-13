import threading

import redis

from monitor_server.models.model_006_tasks import TaskTrackingRecord, db
from monitor_server.settings.conf import RedisConn


class GlobalID:
    def __init__(self):
        last = db.session.query(TaskTrackingRecord.id).order_by(TaskTrackingRecord.id.desc()).first()
        if not last:
            self._id = 0
        else:
            self._id = last.id + 1
        self._task_unique_id_lock = threading.Lock()

    def get_id(self):
        with self._task_unique_id_lock:
            res_id = self._id
            self._id += 1
        return res_id


class GlobalIDRedis:
    def __init__(self):
        self.redis = redis.StrictRedis(host=RedisConn.host, port=RedisConn.port, db=RedisConn.db, password=RedisConn.pswd)

    def get_id(self):
        return self.redis.incr('uni_id')


g_task_unique_id = GlobalIDRedis()
