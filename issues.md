# jiliang_monitor

*集成组后台运维管理系统*

1. QueuePool达到最大连接数问题
    可能是链接未及时释放导致
    也可能是postgres或者sql alchemy设置不当导致
2. 偶尔会出现记录丢失
    丢失之后怎么容错
    如何降低丢失的几率
3. task的前端呈现需要更清晰
    任务起始时间
