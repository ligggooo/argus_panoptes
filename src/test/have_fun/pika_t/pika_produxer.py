#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : pika_produxer.py
# @Time      : 2021/4/20 16:40
# @Author    : Lee
from test.have_fun.pika_t.pika_comsumer import *
import  time

if __name__ == "__main__":
    chan.basic_publish(exchange='',
                          routing_key="test",
                          body=time.ctime(),
                          properties=pika.BasicProperties(delivery_mode=2, content_type="text/xml",
                                                          content_encoding="UTF-8")
                          )

    chan.basic_publish(exchange='',
                       routing_key="test",
                       body="shutdown",
                       properties=pika.BasicProperties(delivery_mode=2, content_type="text/xml",
                                                       content_encoding="UTF-8")
                       )