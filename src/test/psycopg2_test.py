#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : psycopg2.py
# @Time      : 2021/4/6 13:37
# @Author    : Lee

import psycopg2


conn_str = 'user=gpadmin password=xxx dbname=test_pickle_20210207000000_20210208235900_20210204153141 host=172.16.101.118 port=5432'
conn = psycopg2.connect(conn_str)
print(conn)
cur = conn.cursor()
sql = "select task_id,trip_in_task,count(*) from trip_pt group by ( task_id,trip_in_task) order by task_id,trip_in_task"
sql = "select count(*) from trip_pt"
cur.execute(sql)
xx = cur.fetchall()
    #"test_pickle_20210207000000_20210208235900_20210204153141"
print(xx)