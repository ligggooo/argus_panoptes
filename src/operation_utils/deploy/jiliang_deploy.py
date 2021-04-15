#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : jiliang_deploy.py
# @Time      : 2021/3/16 20:19
# @Author    : Lee
from operation_utils.dockers import tar_and_cp_file_2_container, exec_cmd, write_content_2_container
from concurrent.futures import as_completed, ThreadPoolExecutor

src_dir_sys = r"E:\workspace\jiliang_system"
src_dir_proc = r"E:\workspace\jiliang_monitor_pr\src\jiliang_process"
src_dir_semantics = r"E:\workspace\distributed_semantics"
src_dir_trajectory = r"E:\workspace\automapbuilding_z"
master_script = "run_master.sh"
slave_script = "run_slave.sh"
import tarfile


def deploy_to_machine(host, dockers):
    for d in dockers:
        res = exec_cmd(host, 2375, d, "rm -rfv /workspace")
        if res[0] != "success":
            print(res)
        res = exec_cmd(host, 2375, d, "rm -rfv /app/inte_dir")
        if res[0] != "success":
            print(res)
        print(host, d, src_dir_sys)
        tar_and_cp_file_2_container(host, 2375, d, src_dir_sys)
        print(host, d, src_dir_proc)
        tar_and_cp_file_2_container(host, 2375, d, src_dir_proc)
        print(host, d, src_dir_semantics)
        tar_and_cp_file_2_container(host, 2375, d, src_dir_semantics)
        print(host, d, src_dir_trajectory)
        tar_and_cp_file_2_container(host, 2375, d, src_dir_trajectory)
        content = open(r"E:\workspace\jiliang_monitor_pr\src\operation_utils\deploy\jiliang_docker_run.sh", "r",
                       newline="\n").read().replace("\r\n", "\n")
        print(write_content_2_container(host, 2375, d, content, file_path="/run.sh"))


container_list = [
    {
        "host": "172.16.100.51",
        "dockers": ["jiliang_core", "jiliang_slave"],
        "group":["product"]
    },
    {
        "host": "172.16.100.52",
        "dockers": ["jl_slave_52_1", "jl_slave_52_2"],
        "group":["product"]
    },
    {
        "host": "172.16.100.220",
        "dockers": ["jl_slave_220_1"],
        "group":["product"]
    },
    {
        "host": "172.16.101.118",
        "dockers": ["jl_slave_118_1"],
        "group":["product"]
    },
    {
        "host": "172.16.101.119",
        "dockers": ["jl_slave_119_1"],
        "group":["product"]
    },
    # -----------------------------------------------------
    {
        "host": "172.16.100.141",
        "dockers": ["test_container_141"],
        "group":["test"]
    },
    {
        "host": "172.16.100.142",
        "dockers": ["test_container_142"],
        "group":["test"]
    },
    {
        "host": "172.16.100.143",
        "dockers": ["test_container_143"],
        "group":["test"]
    },
    {
        "host": "172.16.100.144",
        "dockers": ["test_container_144"],
        "group":["test"]
    },
    {
        "host": "172.16.100.145",
        "dockers": ["test_container_145"],
        "group":["test"]
    },
]


def check(item):
    filter_list = [
        "172.16.100.141",
        "172.16.100.142",
        "172.16.100.143",
        "172.16.100.144",
        "172.16.100.145"
    ]
    return item["host"] in filter_list


def check_in_group(item, group):
    return group in item["group"]


if __name__ == "__main__":
    pool = ThreadPoolExecutor(1)
    t_v = []
    for item in container_list:
        if check_in_group(item, "test"):
            # t = pool.submit(deploy_to_machine, item["host"], item["dockers"])
            # t_v.append(t)
            pass
        else:
            print(item, "不满足过滤条件")
    for t in as_completed(t_v):
        print(t.result())
