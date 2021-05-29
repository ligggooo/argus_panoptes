#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : api_logger.py
# @Time      : 2021/4/23 16:22
# @Author    : Lee
from logging import StreamHandler, DEBUG, Formatter, getLogger

PROD_LOG_FORMAT = '[%(asctime)s] [PERFORMANCE] in [%(module)s]:[%(funcName)s]: %(message)s'

debug_handler = StreamHandler()
debug_handler.setLevel(DEBUG)
debug_handler.setFormatter(Formatter(PROD_LOG_FORMAT))



server_perf_logger = getLogger("server_perf_logger")
server_perf_logger.setLevel(DEBUG)
# just in case that was not a new logger, get rid of all the handlers
# already attached to it.

server_perf_logger.addHandler(debug_handler)


def test():
    import logging
    l = logging.getLogger("server_perf_logger")
    l.debug("213133")

if __name__ == "__main__":
    test()