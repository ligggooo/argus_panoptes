#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : time_anl.py
# @Time      : 2021/4/16 13:05
# @Author    : Lee
"""

"""

import psycopg2
import matplotlib.pyplot as plt
import numpy,time

dsn = "postgresql://postgres:123456@10.130.160.114:60030/my_test"
con = psycopg2.connect(dsn)

parent_id = "610993"

cur = con.cursor()
sql = f"""
SELECT c.delta,c.sub_id,c.t from 
	(select a.sub_id as sub_id, a.timestamp,b.timestamp,b.timestamp-a.timestamp as delta,a.timestamp as t from 
		(SELECT sub_id,timestamp,state from task_track where parent_id='{parent_id}' and state='0') as a 
			join 
		(SELECT sub_id,timestamp,state from task_track where parent_id='{parent_id}' and state='1') as b 
			on 
		a.sub_id=b.sub_id
	) as c order by c.sub_id;
"""
cur.execute(sql)
res = cur.fetchall()
con.close()




x = numpy.array([float(c[1]) for c in res])
d = numpy.array([float(c[0]) for c in res])
t = numpy.array([c[2] for c in res])
t = t - t.min()
t = t/3600

for r in res:
    print(r)

plt.figure(1)
plt.plot(t, d)

plt.figure(2)
plt.plot(t, t)

plt.show()