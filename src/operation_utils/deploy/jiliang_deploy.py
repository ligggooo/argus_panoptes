#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : jiliang_deploy.py
# @Time      : 2021/3/16 20:19
# @Author    : Lee
from dockers import tar_and_cp_file_2_container

src_dir_sys = "E:\workspace\jiliang_system"
src_dir_proc = "E:\workspace\jiliang_monitor_pr\src\jiliang_process"
import tarfile



if __name__ == "__main__":
    host = "172.16.100.51"
    tar_and_cp_file_2_container(host, 2375, "jiliang_core", src_dir_sys)
    tar_and_cp_file_2_container(host, 2375, "jiliang_core", src_dir_proc)