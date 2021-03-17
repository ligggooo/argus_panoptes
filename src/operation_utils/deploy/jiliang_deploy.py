#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : jiliang_deploy.py
# @Time      : 2021/3/16 20:19
# @Author    : Lee
from dockers import tar_and_cp_file_2_container

src_dir_sys = r"E:\workspace\jiliang_system"
src_dir_proc = r"E:\workspace\jiliang_monitor_pr\src\jiliang_process"
src_dir_semantics = r"E:\workspace\distributed_semantics"
src_dir_trajectory = r"E:\workspace\automapbuilding_z"
import tarfile



if __name__ == "__main__":
    host = "172.16.100.51"
    tar_and_cp_file_2_container(host, 2375, "jiliang_core", src_dir_sys)
    tar_and_cp_file_2_container(host, 2375, "jiliang_core", src_dir_proc)
    tar_and_cp_file_2_container(host, 2375, "jiliang_core", src_dir_semantics)
    tar_and_cp_file_2_container(host, 2375, "jiliang_core", src_dir_trajectory)

    tar_and_cp_file_2_container(host, 2375, "jiliang_slave", src_dir_sys)
    tar_and_cp_file_2_container(host, 2375, "jiliang_slave", src_dir_proc)
    tar_and_cp_file_2_container(host, 2375, "jiliang_slave", src_dir_semantics)
    tar_and_cp_file_2_container(host, 2375, "jiliang_slave", src_dir_trajectory)