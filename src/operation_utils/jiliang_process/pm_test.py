from jiliang_process.process_monitor import

def A():
    return "A"

def B(a):
    d1 = D(1)
    d2 = D(2)
    return a+"B"+d1+d2

def C(b):
    return b+"C"

def D(x):
    return "D%d"%x

def main():
    a= A()
    b = B(a)
    c = C(b)
    print(c)

main()