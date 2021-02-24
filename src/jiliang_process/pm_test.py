from jiliang_process.process_monitor import task_monitor,StatePoint
from jiliang_process.workloads import A,B,C
import traceback




__version__ = "语义算法v 1.0.0"


@task_monitor.cross_system_deco(__version__)
def main(sub_id, parent_id=""):  # 跨系统调用关联
    try:
        a = A()
    except Exception as e:
        print(e)
        a = "error"
    b = B(a)
    c = C(b)
    print(c)


def call(id): # 模拟jiliang系统调用语义脚本的过程
    task_monitor.root_log(id=id, state=StatePoint.start.value)
    try:
        main(sub_id="1", parent_id=id)
        main(sub_id="2", parent_id=id)
        main(sub_id="3", parent_id=id)
    except Exception as e:
        task_monitor.root_log(id=id, state=StatePoint.error.value, desc=traceback.format_exc())
        raise e
    task_monitor.root_log(id=id, state=StatePoint.end.value)


call("20200413004000_20201110232523_20201114112585")
call("20200413004000_20201110232523_20201114112586")