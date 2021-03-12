import sys
import multiprocessing as mp
import subprocess
import threading as th

def xx():
    import import_flush
    pass

# sys.stdout.flush()
# p = th.Thread(target=xx)
# p.start()
#
#
# x = sys.stderr
# for i in range(1000):
#     x.write("%d 123\n"%i)
#     x.flush()
# print(x)
# print(dir(x))
# xx()
#
# p.join()


sb_p = subprocess.Popen(
    ['python', 'import_flush.py'],
    shell=False,
    stdin=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True
)
x = sb_p.wait()
print(x)
print(sb_p.stderr.read())

print("File \"E:\workspace\jiliang_monitor_pr\src\jiliang_process\process_logger.py\", line 12")
