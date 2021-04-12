#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   simple_tornado.py
@Time    :   2021/04/12 22:47:07
@Author  :   Lee 
@Version :   1.0
@Contact :   null@null.com
@License :   None
@Desc    :   None
'''

# here put the import lib
import tornado.ioloop
import tornado.web

x=1
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global x
        y = x 
        x += 1
        self.write(str(y))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    tornado.ioloop.IOLoop.current().start()