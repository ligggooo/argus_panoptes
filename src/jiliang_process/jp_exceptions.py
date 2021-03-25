#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : jp_exceptions.py
# @Time      : 2021/3/24 15:48
# @Author    : Lee


class ProcessShutDownException(Exception):
    def __init__(self, data, msg):
        super().__init__(str(msg))
        self.data = data
        self.msg = msg


class ProcessAccidentallyShutDownException(ProcessShutDownException):
    pass


class ProcessIntentionallyShutDownException(ProcessShutDownException):
    pass


if __name__ == "__main__":

    try:
        import json
        msg = ["1231",{"a":123,"b":3434}]
        raise  ProcessIntentionallyShutDownException(data=msg,msg=1)
    except ProcessShutDownException as e:
        print(e)
        print(e.data)