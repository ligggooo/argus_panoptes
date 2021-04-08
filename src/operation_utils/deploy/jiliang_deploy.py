#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : jiliang_deploy.py
# @Time      : 2021/3/16 20:19
# @Author    : Lee
from operation_utils.dockers import tar_and_cp_file_2_container, exec_cmd

src_dir_sys = r"E:\workspace\jiliang_system"
src_dir_proc = r"E:\workspace\jiliang_monitor_pr\src\jiliang_process"
src_dir_semantics = r"E:\workspace\distributed_semantics"
src_dir_trajectory = r"E:\workspace\automapbuilding_z"
master_script = "run_master.sh"
slave_script = "run_slave.sh"
import tarfile


def deploy_to_machine(host,dockers):
    for d in dockers:
        res = exec_cmd(host, 2375, d,"rm -rf /workspace/*")
        if res[0]!="success":
            print(res)
        print(host,d,src_dir_sys)
        tar_and_cp_file_2_container(host, 2375, d, src_dir_sys)
        print(host, d, src_dir_proc)
        tar_and_cp_file_2_container(host, 2375, d, src_dir_proc)
        print(host, d, src_dir_semantics)
        tar_and_cp_file_2_container(host, 2375, d, src_dir_semantics)
        print(host, d, src_dir_trajectory)
        tar_and_cp_file_2_container(host, 2375, d, src_dir_trajectory)

if __name__ == "__main__":
    host = "172.16.100.51"
    dockers = ["jiliang_core", "jiliang_slave"]
    deploy_to_machine(host, dockers)

    host = "172.16.101.220"
    dockers = ["jl_slave_220_1"]
    deploy_to_machine(host, dockers)
    #
    host = "172.16.101.118"
    dockers = ["jl_slave_118_1"]
    deploy_to_machine(host, dockers)

    host = "172.16.101.119"
    dockers = ["jl_slave_119_1"]
    deploy_to_machine(host, dockers)