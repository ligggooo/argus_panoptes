#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : celery_app.py
# @Time      : 2021/4/15 17:19
# @Author    : Lee

from celery import Celery
class Redis_Conn:
    redis_host = "172.16.100.53"
    redis_port = "6379"
    redis_passwd = "123456"
    db_id = "10"


app = Celery('xx',
             broker='redis://:' + Redis_Conn.redis_passwd + '@' + Redis_Conn.redis_host + ":" + Redis_Conn.redis_port + "/" + Redis_Conn.db_id,
             backend='redis://:' + Redis_Conn.redis_passwd + '@' + Redis_Conn.redis_host + ":" + Redis_Conn.redis_port + "/" + Redis_Conn.db_id,
             include="tasks"
             )


app.start(["worker", "-c", "1", "-E", "--loglevel=info"])