#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/opt/hadoop-3.3.6
export HIVE_HOME=/opt/apache-hive-3.1.3-bin
export PATH=$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin:$PATH

echo "[1/4] 更新 IP 映射..."
sudo /home/root1/heart-disease-system/scripts/update-hosts.sh

echo "[2/4] 启动 Hadoop..."
start-dfs.sh
start-yarn.sh
sleep 5

echo "[3/4] 启动 HiveServer2..."
nohup hive --service hiveserver2 > /tmp/hive.log 2>&1 &
sleep 3

echo "[4/4] 完成"
jps
