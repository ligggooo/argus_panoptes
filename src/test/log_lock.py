import logging
import subprocess
import sys
import time

x= logging.Logger("123")
sh1 = logging.StreamHandler(sys.stdout)
x.addHandler(sh1)
sh2 = logging.StreamHandler(sys.stderr)
x.addHandler(sh2)
sh3 = logging.StreamHandler(sys.stderr)
x.addHandler(sh3)
sh4 = logging.StreamHandler(sys.stderr)
x.addHandler(sh4)

y = 2
print(id(x), id(y))

from jiliang_process.process_monitor import task_monitor
task_monitor.re_config(MONITOR_DISABLED=True)


@task_monitor.root_deco("测试起点")
def main():
    sb_p = subprocess.Popen(
        ['python', 'test_load.py', str(task_monitor.root_id), str(task_monitor.current_id)],
        shell=False,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    msg_a = b''
    sb_p.wait()
    # while 1:
    #     time.sleep(0.1)
    #     xx = sb_p.poll()
    #     if xx == 0:
    #         while 1:
    #             msg = sb_p.stderr.read()
    #             if msg:
    #                 msg_a += msg
    #             else:
    #                 break
    #         break
    #     msg = sb_p.stderr.read()
    #     if msg:
    #         msg_a += msg
    # l=len(msg_a)
    print(l)
    # x = sb_p.wait()
    # print(x, sb_p.stderr.read())


main()
