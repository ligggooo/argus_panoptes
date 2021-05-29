# 集成部署模块

目前此功能只是在一些基础的docker操作上进行了封装，可以保证在需要批量创建和更新计算集群时提高效率，并减少人为错误。

尚未与数据库打通，也没有和运维系统web后端集成，还是一个初级版本。

## 部署脚本和“组”

operation_utils/deploy/jiliang_deploy.py


****
**脚本的执行依赖一个描述执行单元的字典列表，如下所示：**

```
container_list = [
    # ------------ 旧机器上的生产节点组---------------------
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
    ...
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
```

其中每一个元素代表一个可被部署的单元，这个单元有host ip和容器名两个字段（dockers），代表部署在这台机器上的若干个container。

每个单元可以被编入至少一个group，每次批量操作实际上是针对一个group进行的。

core是一个标记，core为True表明这个单元在本group中的角色是master，部署脚本会对master节点做一些特殊的设置。


根据情况来注释和打开一些代码行来运行这个脚本，可以完成构图系统的部署。
```
if __name__ == "__main__":
    # ---------------------------------测试环境------------------------------
    # create_group_containers()
    # deploy_system()
    # ---------------------------------生产环境------------------------------
    deploy_system(group="product", enable_monitor=True, runtime_mode="dev_new")
    # create_group_containers(group="product")
    # -----------------------------------------------------------------------
    deploy_system(group="product_2", enable_monitor=True, runtime_mode="dev_new")
    # create_group_containers(group="product_2")
    # -----------------------------------------------------------------------
    # deploy_system(group="product_3", enable_monitor=True, runtime_mode="dev_new")
    # create_group_containers(group="product_3")
```


## 环境变量的设置

```
deploy_system(group="product_2", 
    enable_monitor=True, 
    runtime_mode="dev_new")
```

+ 监控器开关 enable_monitor
+ 运行模式  runtime_mode


这两个参数会影响到docker容器中的环境变量 “MONITOR_ENABLED”和“RUNTIME_MODE”。
MONITOR_ENABLED 会决定监控器客户端是否工作；
RUNTIME_MODE 则会决定系统使用哪一组配置文件，进而影响到各个模块的具体设置。

## 容器的启动脚本

>operation_utils/deploy/jiliang_docker_run_template.sh  
在被环境变量设置语句填充之后会被写入docker容器中的启动脚本  
> /run.sh


/run.sh
```
sh /workspace/jiliang_system/deploy/install.sh
sh /workspace/jiliang_monitor_pr/src/jiliang_process/deploy/install.sh
sh /workspace/jiliang_system/deploy/automapbuilding_z/install.sh
sh /workspace/jiliang_system/deploy/distributed_semantics/install.sh
# 项目中每一个组成模块都有自己的 install.sh脚本

sh /workspace/jiliang_system/deploy/run.sh
# jiliang_system/deploy/run.sh 负责启动celery和logstash
```
