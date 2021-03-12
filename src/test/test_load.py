import logging,sys
from jiliang_process.process_monitor import task_monitor
task_monitor.re_config(MONITOR_DISABLED=False)

x= logging.Logger("123")
# print("---------11111----------", x.handlers)
sh1 = logging.StreamHandler(sys.stdout)
x.addHandler(sh1)
sh2 = logging.StreamHandler(sys.stdout)
x.addHandler(sh2)
sh3 = logging.StreamHandler(sys.stderr)
x.addHandler(sh3)
# sh4 = logging.StreamHandler(sys.stderr)
# x.addHandler(sh4)

y = 2
# print(id(x), id(y))

# print("--------22222--------", x.handlers)


@task_monitor.cross_process_deco("工作负载")
def work_load(root_id,parent_id):
    for i in range(1000):
        # x.info("12345678")
        task(i)


@task_monitor.normal_task_deco("被循环了10000次的任务")
def task(i):
    sys.stderr.write("err %d\n"%i)
    sys.stderr.flush()
    print("std 中文 x", i)

print("sys argv",sys.argv)
_,a,b = sys.argv
# _,a,b = sys.argv = [1,2,3]
work_load(root_id=a, parent_id=b)