from jiliang_process.process_monitor import task_monitor,StatePoint
from jiliang_process.workloads import normal_task_throws_exception,normal_task_with_a_loop,normal_task_starts_multiple_threads,xp_test
import traceback




__version__ = "语义算法v 1.0.0"


@task_monitor.cross_process_deco(__version__)
def main(sub_id, parent_id="",batch_id=None):  # 跨系统调用关联
    try:
        a = normal_task_throws_exception()
    except Exception as e:
        print(e)
        a = "error"
    b = normal_task_with_a_loop(a)
    c = normal_task_starts_multiple_threads(b)
    try:
        xp_test(parent_id=task_monitor.get_current_call_stack_node().this_id,batch_id=batch_id)
    except Exception as e:
        print(e)
        raise e
    print(c)

@task_monitor.cross_process_deco(__version__)
def main2(sub_id, parent_id="",batch_id=None):  # 跨系统调用关联
    try:
        a = normal_task_throws_exception()
    except Exception as e:
        print(e)
        a = "error"
    b = normal_task_with_a_loop(a)
    c = normal_task_starts_multiple_threads(b)

    print(c)

def call(id): # 模拟jiliang系统调用语义脚本的过程
    from monitor_server.models.model_006_tasks import db
    db.metadata.clear()
    from monitor_server.models.model_006_tasks import Task
    new_task = Task(task_id=id,desc="测试任务")
    sess = db.session()
    sess.add(new_task)
    sess.commit()
    sess.close()
    task_monitor.manual_log(id=id, state=StatePoint.start.value, batch_id=id)
    try:
        main(sub_id="1", parent_id=id, batch_id=id)
        main(sub_id="2", parent_id=id, batch_id=id)
        main(sub_id="3", parent_id=id, batch_id=id)
    except Exception as e:
        task_monitor.manual_log(id=id, state=StatePoint.error.value, batch_id=id, desc=traceback.format_exc())
        raise e
    task_monitor.manual_log(id=id, state=StatePoint.end.value, batch_id=id)


def test_main():
    import uuid
    id1 = str(uuid.uuid4())
    call(id1)
    id2 = str(uuid.uuid4())
    call(id2)



@task_monitor.normal_task_deco
def test_main_single_machine_single_thread():
    normal_task_with_a_loop("xxxx")
    normal_task_throws_exception()


@task_monitor.normal_task_deco
def test_main_single_machine_multiple_threads():
    normal_task_starts_multiple_threads("xxxx")
    normal_task_throws_exception()

# test_main_single_machine_single_thread()

test_main_single_machine_multiple_threads()