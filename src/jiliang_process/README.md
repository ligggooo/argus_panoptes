# 任务监控系统客户端使用说明

任务监控系统将函数调用、脚本调用、分布式调用等等统一抽象为“过程”，监控器将这些具有层级关系的过程的执行状态记录下来，并通过web页面的形式呈现。

## 客户端通过一组装饰器与后端进行交互，并记录状态信息

将这些装饰器添加上需要监控的函数上，即可通过任务监控系统服务端（http://172.16.101.220:60010/tasks ） 跟踪到这个函数的“开始”、“结束”和“异常”这三种状态。


        ```
        from jiliang_process.process_monitor import task_monitor

        @task_monitor.normal_task_deco(name="一个简单的需要被监控的函数")
        def normal_task(alpha):
            # do something
            pass

        ```

任务跟踪器默认是关闭的，即不会影响原本代码的行为。需要设置环境变量才能启用； 

         MONITOR_ENABLED=1 




## 目前一共针对不同的应用场景实现了四种“过程装饰器”，分别是: 

+ "cross_thread_deco"和 "normal_task_deco"：普通函数装饰器和跨线程装饰器 

    使用的时候只需要将其添加到被监控函数上即可：

    ```
    # "cross_thread_deco"和 "normal_task_deco"支持一个参数name，如果不填，被记录下来的过程名就是函数名
    @task_monitor.normal_task_deco("一个带循环的任务")
    def normal_task_with_a_loop(alpha):
        """
        normal_task_with_a_loop test
        :param alpha:
        :return:
        """ 
        pass
    ```

+ "root_deco": 根任务装饰器，放置到你认为能标识任务起点的函数上，一次任务只能历经一个根节点。

    可以放置在jiliang_system的构图任务启动回调函数上，或者是本地调试时的main函数上。
    ```
    @task_monitor.root_deco("一个测试根任务", "param1_batch_id")
    def call_root(param1_batch_id):
        pass

    call_root(param1_batch_id="batch001")

    """
    root_deco 支持两个参数：
        第一个参数是这个根任务的统一名称；
        第二个参数是你计划用来区分这个批次任务的变量名————装饰器从你传给call_root的参数列表里面取出"param1_batch_id"这个变量的值作为这个任务的批次标记。
    这个任务在跟踪系统里面的全名就是：
               “ 一个测试根任务 <batch001:2106> ”
    这里的2106是系统内部为此次根任务分配的id。
    """
    ```


+ "cross_process_deco": 跨进程装饰器，放置到被跨进程调用的函数上。 
    
        这里的“被跨进程调用的函数”不必是严格的被调用函数，可以是被跨进程调用的函数的某一个子函数。 下面的例子中，celery task judge_whether_to_launch_semantic的子函数 judge_whether_to_launch_semantic_workload被加上了这个装饰器，于是成为了jiliang_system的调度任务的子任务，被任务跟踪系统关联在了一起。

    *被监控的跨进程的任务调用需要遵守一个规范——必须有root_id和parent_id两个关键字参数。这也是目前的设计中唯一需要对被监控代码做侵入式改造的地方。*

        以jiliang_system通过celery调用distributed_semantics为例：

    ```
    #   调用方代码

    #   ---手动为judge_whether_to_launch_semantic增加了两个参数----------
    #   --                root_id 和 parent_id                       --
    #   -- 这两个变量的值都是直接从客户端提供的task_monitor中获得 ---------
    argv_str_json_obj = json.loads(argv_str)
    argv_str_json_obj.update({"root_id":task_monitor.root_id,"parent_id":task_monitor.current_id})
    argv_str = json.dumps(argv_str_json_obj)
     #   --------------------------------------------------------------
    task_handler = solo_tasks.judge_whether_to_launch_semantic.delay(argv_str)
    ```

    ```
    #   被调用方代码

    # 函数内部做了一层适配，将root_id 和 parent_id 抽取出来作为参数
    # 传给judge_whether_to_launch_semantic_workload
    @app.task
    def judge_whether_to_launch_semantic(argv_str):
        message_obj = json.loads(argv_str)
        root_id = message_obj.get("root_id")
        parent_id = message_obj.get("root_id")
        status,msg_str = judge_whether_to_launch_semantic_workload(argv_str,root_id=root_id, parent_id=parent_id)
        return status,msg_str

    # 监控器装饰器，被监控的跨进程调用实际上是 
    # “judge_whether_to_launch_semantic_workload”
    @task_monitor.cross_process_deco("跨celery调用判断是否启动语义")
    def judge_whether_to_launch_semantic_workload(argv_str,root_id, parent_id):
        running_start = time.strftime('%Y-%m-%d %H:%M:%S')
        t1 = time.time()
        except_log = ""
        message_obj = json.loads(argv_str)
    ```

## 监控脚本启动器的引入
有时候，被监控对象不希望被插入任何代码，即监控器对被监控对象来说完全不可见。

为了满足这种需求，我们引入了脚本启动器，使用import hacking的方式改变被监视模块的行为。
脚本启动器的配置说明见
>[src/jiliang_process/boot/README.md](/src/jiliang_process/boot/README.md)

