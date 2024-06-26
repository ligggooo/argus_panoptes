#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : db_utils.py
# @Time      : 2021/3/25 15:01
# @Author    : Lee

from monitor_server import db
import traceback


def wake_up_data_base():
    try:
        sess = db.session()
        xx = sess.execute("select * from pg_ts_config")
        print(xx.fetchall())
        sess.close()
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        try:
            sess = db.session()
            xx = sess.execute("select * from pg_ts_config")
            print(xx.fetchall())
            sess.close()
        except Exception as e:
            traceback.print_exc()
            raise e


if __name__ == "__main__":
    wake_up_data_base()
