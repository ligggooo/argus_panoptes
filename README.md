# argus panoptes

*An unified monitor system for distributed systems*

## 依赖包
jiliang_monitor服务端依赖
- APScheduler==3.7.0
- docker==5.0.0
- Flask==1.1.2
- Flask-APScheduler==1.12.2
- Flask-Cors==3.0.10
- Flask-SQLAlchemy==2.5.1
- Jinja2==2.11.3
- psycopg2==2.8.6
- requests==2.25.1
- SQLAlchemy==1.4.11

jiliang_monitor客户端依赖
- requests==2.25.1

## 服务器启动
```
nohup python -u monitor_server/run.py >/home/lee/monitor_server.log 2>&1 &
```

## 目录结构
```
src/
  jiliang_process/              过程跟踪客户端
    boot/                           脚本启动器
      starter.py                        脚本启动器主程序
      start_conf.ini                    脚本启动器配置文件
    deploy/                         客户端 部署相关脚本
    jlp_release_package/            客户端对外接口，直接使用监控器的代码需包含此包
      process_monitor.py              客户端对外接口
    **                              其他核心文件
    README.md                       客户端使用说明
  monitor_server/               监控器服务端
    api/                            各子模块视图函数
      api_utils/                        与视图关系紧密，但过于复杂的一些方法
    models/                         模型层，使用orm定义
    settings/                       配置文件
    static/                         静态文件
    templates/                      html模板
  operation_utils/              运维相关函数形成的包
    deploy/                         构图系统集成部署模块
    dockers.py                      封装docker操作
  test/                         测试
```

## 说明文档路径
> 总文档(本文档)  > src/README.md

> 过程跟踪客户端使用文档 > [src/jiliang_process/README.md](src/jiliang_process/README.md)

> 脚本启动器使用文档 > [src/jiliang_process/boot/README.md](src/jiliang_process/boot/README.md) 

> 集成部署模块使用文档 > [src/operation_utils/deploy/README.md](src/operation_utils/deploy/README.md)
 