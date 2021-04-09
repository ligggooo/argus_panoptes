#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : new_docker.py
# @Time      : 2021/4/9 10:16
# @Author    : Lee
from operation_utils.dockers import create_container,pull_image

pull_image("172.16.100.52")

if __name__ == "__main__":
    pass