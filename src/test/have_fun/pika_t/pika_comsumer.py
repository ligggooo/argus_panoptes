#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : pika_comsumer.py
# @Time      : 2021/4/20 16:37
# @Author    : Lee

import pika
import time
import multiprocessing

RABBITMQ_USER = 'admin'
RABBITMQ_PASSWORD = '123456abc'
RABBITMQ_IP = '172.16.100.10'
RABBITMQ_PORT = 5672


def on_msg(channel, method_frame, header_frame, body):
    print("start",body)
    if body.decode("ascii") == "shutdown":
        exit(0)
    time.sleep(2)
    print("end", body)

p = multiprocessing.current_process()
print(p.pid)

user_pwd = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_IP, port=RABBITMQ_PORT,
    credentials=user_pwd))
chan = conn.channel()



if __name__ == "__main__":
    chan.queue_declare(queue="test", durable=True)
    chan.basic_consume("test", on_msg, auto_ack=True)
    chan.start_consuming()
