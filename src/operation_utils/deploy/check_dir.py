#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : check_dir.py
# @Time      : 2021/4/9 9:50
# @Author    : Lee
import os

from operation_utils.dockers import tar_and_cp_file_2_container, exec_cmd, cp_file_from_container

dir_temp = "/app/inte_dir/%s/jiliang_system"
def check_dir(host, dockers, dir_mod=dir_temp, search="183125"):
    collect_local = []
    for d in dockers:
        dir = dir_mod%(d)
        status, res = exec_cmd(host,2375,d,"ls %s"%dir)
        if status != "success":
            print(host,d,res)
        for s in res.decode("utf-8").split("\n"):
            if s.replace(".txt","").endswith(search) or search in s:
                print(host,d,s)
                file = "%s/%s"%(dir, s)
                collect_local.append((host,d,file))

    return collect_local


if __name__ == "__main__":
    collector = []
    host = "172.16.100.51"
    dockers = ["jiliang_core", "jiliang_slave"]
    collector.extend(check_dir(host, dockers))

    host = "172.16.100.52"
    dockers = ["jl_slave_52_1", "jl_slave_52_2"]
    collector.extend(check_dir(host, dockers))

    host = "172.16.101.220"
    dockers = ["jl_slave_220_1"]
    collector.extend(check_dir(host, dockers))
    #
    host = "172.16.101.118"
    dockers = ["jl_slave_118_1"]
    collector.extend(check_dir(host, dockers))

    host = "172.16.101.119"
    dockers = ["jl_slave_119_1"]
    collector.extend(check_dir(host, dockers))

    print(collector)

    input("收集？")
    for item in collector:
        cp_file_from_container(item[0], 2375, item[1], item[2], tmp_dir_root="E:/data")

