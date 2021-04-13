#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   simple_server.py
@Time    :   2021/04/12 22:16:56
@Author  :   Lee 
@Version :   1.0
@Contact :   null@null.com
@License :   None
@Desc    :   None
'''

# here put the import lib
from flask import Flask
import time
from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()
app = Flask("test")

x = 0
@app.route("/",methods=["get"])
def hello():
    global x
    y = x
    x += 1
    # time.sleep(1)
    return str(y)


server = WSGIServer(('127.0.0.1', int(5001)), app)
server.serve_forever()
# app.run(host="127.0.0.1", port=5001)