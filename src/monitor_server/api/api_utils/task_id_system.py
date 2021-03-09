import threading

from monitor_server.models.model_006_tasks import TaskTrackingRecord

class GlobalID:
    def __init__(self):
        last = TaskTrackingRecord.query.order_by(TaskTrackingRecord.id.desc()).first()
        if not last:
            self._id = 0
        else:
            self._id = last.id+1
        self._task_unique_id_lock = threading.Lock()

    def get_id(self):
        with self._task_unique_id_lock:
            res_id = self._id
            self._id += 1
        return res_id

g_task_unique_id = GlobalID()