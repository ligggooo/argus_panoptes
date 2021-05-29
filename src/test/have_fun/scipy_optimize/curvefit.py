#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : curvefit.py
# @Time      : 2021/4/23 11:04
# @Author    : Lee
import matplotlib.pyplot as plt
import numpy
from scipy.optimize import curve_fit

x = numpy.linspace(0, 10, 100)

def line(x, k, b):
    y = k * x + b
    return y

def line2(x,r):
    return numpy.sqrt(r**2-x**2)

# y = numpy.ones(x.shape) * 5 + numpy.random.randn(100) * 0.1

y = line(x,0,5) + numpy.random.randn(100) * 0.1
y = line2(x,10) + numpy.random.randn(100) * 0.1

popt, pcov = curve_fit(line2, x, y, bounds=(0, 20))
print(popt, pcov)

y2 = line2(x, *popt)

plt.figure(1)
# plt.axes(aspect="equal")
# plt.axhspan(ymin=0, ymax=10, xmin=0, xmax=10)
plt.scatter(x, y)
plt.plot(x, y2, "r")

plt.show()

if __name__ == "__main__":
    pass
