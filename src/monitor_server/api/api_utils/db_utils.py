#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : db_utils.py
# @Time      : 2021/3/25 15:01
# @Author    : Lee

from monitor_server import db


def wake_up_data_base():
    sess = db.session()
    xx = sess.execute("select * from wake_up")
    print(xx.fetchall())
    pass


if __name__ == "__main__":
    wake_up_data_base()
