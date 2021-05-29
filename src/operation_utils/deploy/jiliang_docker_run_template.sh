echo "========================================="
echo $?
echo "========================================="
sh /workspace/jiliang_system/deploy/install.sh
echo "========================================="
echo $?
echo "========================================="
sh /workspace/jiliang_monitor_pr/src/jiliang_process/deploy/install.sh
echo "========================================="
echo $?
echo "========================================="
sh /workspace/jiliang_system/deploy/automapbuilding_z/install.sh
echo "========================================="
echo $?
echo "========================================="
sh /workspace/jiliang_system/deploy/distributed_semantics/install.sh
echo "========================================="
echo $?
echo "========================================="

source ~/.bashrc
{% env_set %}

sh /workspace/jiliang_system/deploy/run.sh
echo "========================================="
echo $?
echo "========================================="


{% core_cmd %}


/bin/bash