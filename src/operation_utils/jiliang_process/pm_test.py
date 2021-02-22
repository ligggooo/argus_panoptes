from jiliang_process.process_monitor import ProcessMonitor,ProcessMonitor_Concurrent
from threading import Thread
import time


@ProcessMonitor
def A():
    return "A"

@ProcessMonitor
def B(a):
    d1 = D(1)
    d2 = D(2)
    return a+"B"+d1+d2

@ProcessMonitor
def C(b):
    tl = []
    for i in range(10):
        t= Thread(target=E,args=("e",))
        tl.append(t)
    [t.start() for t in tl]
    [t.join() for t in tl]
    return b+"C"

@ProcessMonitor_Concurrent
def E(c):
    time.sleep(3)
    print(c)

@ProcessMonitor
def D(x):
    return "D%d"%x

@ProcessMonitor
def main():
    a= A()
    b = B(a)
    c = C(b)
    print(c)

main()