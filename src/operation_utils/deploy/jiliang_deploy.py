#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @FileName  : jiliang_deploy.py
# @Time      : 2021/3/16 20:19
# @Author    : Lee
from typing import Dict

from api_utils.portmapping_parser import port_mapping_str2dict
from operation_utils.dockers import tar_and_cp_file_2_container, exec_cmd, write_content_2_container, restart_container, \
    remove_container, create_container
from concurrent.futures import as_completed, ProcessPoolExecutor

src_dir_sys = r"E:\workspace\jiliang_system"
src_dir_proc = r"E:\workspace\jiliang_monitor_pr\src\jiliang_process"
src_dir_semantics = r"E:\workspace\distributed_semantics"
src_dir_trajectory = r"E:\workspace\automapbuilding_z"


container_list = [
    # ------------ 旧机器上的生产节点组-----------------------------------
    {
        "host": "172.16.100.51",
        "dockers": ["jl_core_51_1"],
        "group": ["product"],
        "core": False
    },
    {
        "host": "172.16.100.51",
        "dockers": ["jl_slave_51_2"],
        "group": ["product"],
        "core": False
    },
    {
        "host": "172.16.100.52",
        "dockers": ["jl_slave_52_1", "jl_slave_52_2"],
        "group": ["product"],
        "core": False
    },
    # {
    #     "host": "172.16.100.220",
    #     "dockers": ["jl_slave_220_1"],
    #     "group": ["product"],
    #     "core": False
    # },
    {
        "host": "172.16.101.118",
        "dockers": ["jl_slave_118_1"],
        "group": ["product"],
        "core": False
    },
    {
        "host": "172.16.101.119",
        "dockers": ["jl_slave_119_1"],
        "group": ["product"],
        "core": False
    },
    # ------------------ 新机器上的测试节点组-----------------------------------
    {
        "host": "172.16.100.141",
        "dockers": ["test_container_141"],
        "group": ["test"],
        "core": True
    },
    {
        "host": "172.16.100.142",
        "dockers": ["test_container_142"],
        "group": ["test"],
        "core": False
    },
    {
        "host": "172.16.100.143",
        "dockers": ["test_container_143"],
        "group": ["test"],
        "core": False
    },
    {
        "host": "172.16.100.144",
        "dockers": ["test_container_144"],
        "group": ["test"],
        "core": False
    },
    {
        "host": "172.16.100.145",
        "dockers": ["test_container_145"],
        "group": ["test"],
        "core": False
    },
    # -----------------------------------------------------
    {
        "host": "172.16.100.141",
        "dockers": ["jl_slave_141"],
        "group": ["product_2"],
        "core": True
    },
    {
        "host": "172.16.100.142",
        "dockers": ["jl_slave_142"],
        "group": ["product_2"],
        "core": False
    },
    {
        "host": "172.16.100.143",
        "dockers": ["jl_slave_143"],
        "group": ["product_2"],
        "core": False
    },
    {
        "host": "172.16.100.144",
        "dockers": ["jl_slave_144"],
        "group": ["product_2"],
        "core": False
    },
    {
        "host": "172.16.100.145",
        "dockers": ["jl_slave_145"],
        "group": ["product_2"],
        "core": False
    },
    # -----------------------------------------------------
    {
        "host": "172.16.100.141",
        "dockers": ["jl_slave_141_2"],
        "group": ["product_3"],
        "core": False
    },
    {
        "host": "172.16.100.142",
        "dockers": ["jl_slave_142_2"],
        "group": ["product_3"],
        "core": False
    },
    {
        "host": "172.16.100.143",
        "dockers": ["jl_slave_143_2"],
        "group": ["product_3"],
        "core": False
    },
    {
        "host": "172.16.100.144",
        "dockers": ["jl_slave_144_2"],
        "group": ["product_3"],
        "core": False
    },
    {
        "host": "172.16.100.145",
        "dockers": ["jl_slave_145_2"],
        "group": ["product_3"],
        "core": False
    },
]

images = {
    "test": "172.16.100.51:5000/image_20201218",
    "product": "172.16.100.51:5000/image_20201218",
    "product_2": "172.16.100.51:5000/image_20201218",
    "product_3": "172.16.100.51:5000/image_20201218",
}


def custom_check(item):
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


# ----------------------------------------------------------------------------------------------------------------------


def render(template_name: str, params: Dict):
    content = open(template_name, "r", newline="\n").read().replace("\r\n", "\n")
    for k in params:
        content = content.replace("{%% %s %%}" % k, params[k])
    return content


def deploy_to_machine(host, dockers, core_flag, enable_monitor, runtime_mode=None):
    for d in dockers:
        print(restart_container(host, 2375, d))
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
        env_set = ""
        core_cmd = ""
        if runtime_mode:
            env_set += "export RUNTIME_MODE=%s\n"%runtime_mode
        if enable_monitor:
            env_set += "export MONITOR_ENABLED=1\n"
        if core_flag:
            core_cmd += """
ps -aux |grep celery| awk '{print($2)}' | xargs kill -9
cd $PATH_MAP/jiliang_system
nohup /root/anaconda3/bin/python -u ./main_dist_mapbuilding.py  > ./master_$(date +"%s").log 2>&1 &
            """
        run_content = render(
            r"E:\workspace\jiliang_monitor_pr\src\operation_utils\deploy\jiliang_docker_run_template.sh", {
                "env_set": env_set,
                "core_cmd": core_cmd
            })

        print(write_content_2_container(host, 2375, d, run_content, file_path="/run.sh"))
        print(restart_container(host, 2375, d))


def deploy_system(group="test", enable_monitor=True, runtime_mode="test"):
    pool = ProcessPoolExecutor(5)
    t_v = []
    for item in container_list:
        if check_in_group(item, group):
            t = pool.submit(deploy_to_machine, item["host"], item["dockers"], item["core"],enable_monitor, runtime_mode)
            t_v.append(t)
            # pass
        else:
            print(item, "不满足过滤条件")
    for t in as_completed(t_v):
        print("部署结果", t.result())


def init_container(host_ip, container_id_list, image_name, cmd="sh /run.sh", ports=""):
    port = 2375
    port_mapping = port_mapping_str2dict(ports)
    for container_id in container_id_list:
        remove_container(host_ip, port, container_id)
        c, msg = create_container(host_ip, port, image_name, container_id, cmd,
                                  port_mapping=port_mapping)
        assert (c is not None)


def create_group_containers(group="test"):
    pool = ProcessPoolExecutor(5)
    t_v = []
    for item in container_list:
        if check_in_group(item, group):
            t = pool.submit(init_container, item["host"], item["dockers"], images[group])
            t_v.append(t)
            # pass
        else:
            print(item, "不满足过滤条件")
    for t in as_completed(t_v):
        print(t.result())


if __name__ == "__main__":
    # ------------------------------------测试环境---------------------------------
    # create_group_containers()
    # deploy_system()
    # ------------------------------------生产环境---------------------------------
    deploy_system(group="product", enable_monitor=True, runtime_mode="dev_new")
    # create_group_containers(group="product")
    # -----------------------------------------------------------------------------
    deploy_system(group="product_2", enable_monitor=True, runtime_mode="dev_new")
    # create_group_containers(group="product_2")
    # -----------------------------------------------------------------------------
    # deploy_system(group="product_3", enable_monitor=True, runtime_mode="dev_new")
    # create_group_containers(group="product_3")
