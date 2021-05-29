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
sh /workspace/jiliang_system/deploy/automapbuilding_z/install.sh
echo "========================================="
echo $?
echo "========================================="
sh /workspace/jiliang_system/deploy/distributed_semantics/install.sh
echo "========================================="
echo $?
echo "========================================="

source ~/.bashrc
export RUNTIME_MODE=test
export MONITOR_ENABLED=1

sh /workspace/jiliang_system/deploy/run.sh
echo "========================================="
echo $?
echo "========================================="



cd $PATH_MAP/jiliang_system
nohup /root/anaconda3/bin/python ./launch_dist_master_modify_v3_1.py  > master_$(date +"%s").log 2>&1 &