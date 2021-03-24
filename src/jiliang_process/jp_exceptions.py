#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : jp_exceptions.py
# @Time      : 2021/3/24 15:48
# @Author    : Lee


class ProcessAccidentallyShutDownException(Exception):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":

    try:
        import json
        msg = ["1231",{"a":123,"b":3434}]
        raise  ProcessAccidentallyShutDownException(json.dumps(msg,indent=" "))
    except ProcessAccidentallyShutDownException as e:
        print(e)
        print(json.loads(str(e)))