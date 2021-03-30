echo "========================================="
echo $?
echo "========================================="
sh /workspace/jiliang_monitor_pr/src/jiliang_process/deploy/install.sh 
echo "========================================="
echo $?
echo "========================================="
sh /workspace/jiliang_system/deploy/install.sh
echo "========================================="
echo $?
echo "========================================="
sh /workspace/automapbuilding_z/deploy/install.sh 
echo "========================================="
echo $?
echo "========================================="
sh /workspace/distributed_semantics/deploy/install.sh 
echo "========================================="
echo $?
echo "========================================="


export RUNTIME_MODE=development_lgw
export MONITOR_ENABLED=1

sh /workspace/jiliang_system/deploy/run.sh
echo "========================================="
echo $?
echo "========================================="

