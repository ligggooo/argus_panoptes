#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : is_alive.py
# @Time      : 2021/3/18 9:39
# @Author    : Lee
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# from .settings.conf import TestingConfig
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = Flask("test")
# app.config.from_object("monitor_server.settings.conf.TestingConfig2")
# app.jinja_env.variable_start_string = '[['
# app.jinja_env.variable_end_string = ']]'
# # 将db注册到app中（在内部读取配置文件）    　　
# app.config["SQLALCHEMY_ECHO"] = True
"""
class TestingConfig2(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI="postgresql://postgres:123456@10.130.160.114:60030/my_test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TASK_TRACK_CACHE = False
    TASK_RECORDER_URL = "http://127.0.0.1:60010/record_tasks"
    TASK_UNIQUE_ID_URL = "http://127.0.0.1:60010/task_unique_id"
"""
app.config.update({
    "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:123456@10.130.160.114:60030/my_test",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False
})

db = SQLAlchemy(app)

if __name__ == "__main__":
    import time
    ses = db.session()
    while 1 :
        print(ses.is_active)
        time.sleep(1)