from __future__ import annotations

import os
import subprocess

import pymysql
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PredictionRecord


def _hdfs_tables():
    """Query HDFS to get all Hive warehouse tables with sizes."""
    env = os.environ.copy()
    env['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk-amd64'
    env['HADOOP_HOME'] = '/opt/hadoop-3.3.6'
    env['PATH'] = env['JAVA_HOME'] + '/bin:' + env['HADOOP_HOME'] + '/bin:' + env.get('PATH', '')
    
    try:
        result = subprocess.run(
            ['hdfs', 'dfs', '-du', '-s', '/user/hive/warehouse/heart_disease_system.db/*'],
            capture_output=True, text=True, timeout=15, env=env
        )
        tables = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 3:
                size = int(parts[0])
                path = parts[-1]
                name = path.split('/')[-1]
                tables.append({'name': name, 'size': size})
        return tables
    except Exception:
        return []


class WarehouseView(APIView):
    """GET /api/system/warehouse -- list tables from MySQL (ADS) + HDFS (ODS/DWD)."""

    def get(self, request):
        layers = {'ods': [], 'dwd': [], 'ads': []}
        
        # 1. Get ODS/DWD from HDFS
        hdfs_tables = _hdfs_tables()
        for t in hdfs_tables:
            entry = {'name': t['name'], 'size': t['size'], 'sizeStr': _format_size(t['size'])}
            lower = t['name'].lower()
            if lower.startswith('ods_'):
                entry['description'] = '原始数据 (HDFS/Hive)'
                layers['ods'].append(entry)
            elif lower.startswith('dwd_'):
                entry['description'] = '清洗后数据 (HDFS/Hive)'
                layers['dwd'].append(entry)
        
        # 2. Get ADS from MySQL
        try:
            conn = pymysql.connect(
                host=os.getenv('ADS_MYSQL_HOST', '127.0.0.1'),
                port=int(os.getenv('ADS_MYSQL_PORT', '3306')),
                user=os.getenv('ADS_MYSQL_USER', 'heart_user'),
                password=os.getenv('ADS_MYSQL_PASSWORD', 'heart_password'),
                database='information_schema',
                charset='utf8mb4',
            )
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        'SELECT table_name, table_rows FROM tables WHERE table_schema = %s ORDER BY table_name',
                        ('heart_disease',),
                    )
                    for name, cnt in cur.fetchall():
                        if name.lower().startswith('ads_'):
                            layers['ads'].append({
                                'name': name,
                                'rows': cnt or 0,
                                'description': '应用数据 (MySQL)',
                            })
            finally:
                conn.close()
        except Exception:
            pass
        
        # Remove empty
        layers = {k: v for k, v in layers.items() if v}
        return Response({'layers': layers})


def _format_size(size_bytes):
    if size_bytes >= 1024 * 1024:
        return f'{size_bytes / (1024*1024):.1f} MB'
    if size_bytes >= 1024:
        return f'{size_bytes / 1024:.1f} KB'
    return f'{size_bytes} B'


class ClusterStatusView(APIView):
    """GET /api/system/cluster -- check running services."""

    def get(self, request):
        env = os.environ.copy()
        env['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk-amd64'
        env['PATH'] = env['JAVA_HOME'] + '/bin:' + env.get('PATH', '')

        # JPS
        java_procs = []
        try:
            result = subprocess.run(['jps'], capture_output=True, text=True, timeout=5, env=env)
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 2 and parts[1] != 'Jps':
                    java_procs.append(parts[1])
        except Exception:
            pass

        # Check ports
        port_map = {
            9870: 'HDFS NameNode',
            8088: 'YARN ResourceManager',
            10000: 'Hive Server2',
            3306: 'MySQL',
            8000: 'Django API',
        }
        services = []
        try:
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=5)
            listening = result.stdout
        except Exception:
            listening = ''

        for port, name in port_map.items():
            is_running = f':{port}' in listening
            services.append({'name': name, 'status': 'running' if is_running else 'stopped', 'port': port})

        return Response({'services': services, 'javaProcesses': java_procs})


class PredictionHistoryView(APIView):
    """GET /api/system/predictions -- recent prediction records."""

    def get(self, request):
        qs = PredictionRecord.objects.order_by('-created_at')[:50]
        records = []
        for r in qs:
            records.append({
                'id': r.id,
                'probability': r.probability,
                'riskLevel': r.risk_level,
                'riskLabel': r.risk_label,
                'modelName': r.model_name,
                'createdAt': r.created_at.isoformat(),
                'inputData': r.input_data,
            })
        return Response({'records': records, 'total': PredictionRecord.objects.count()})


class ETLStepsView(APIView):
    """GET /api/system/etl-steps -- ETL pipeline description."""

    def get(self, request):
        steps = [
            {'step': 1, 'name': 'CSV导入HDFS', 'source': '本地CSV文件', 'target': 'HDFS /user/hive/warehouse', 'method': 'hdfs dfs -put', 'status': 'completed'},
            {'step': 2, 'name': 'ODS层建表', 'source': 'HDFS CSV文件', 'target': 'Hive ODS外部表', 'method': 'CREATE EXTERNAL TABLE', 'status': 'completed'},
            {'step': 3, 'name': '数据清洗(DWD)', 'source': 'ODS原始表', 'target': 'DWD清洗表', 'method': 'Hive SQL (去重/空值/类型转换)', 'status': 'completed'},
            {'step': 4, 'name': '特征工程', 'source': 'DWD清洗表', 'target': 'DWD特征采样表', 'method': 'Hive SQL (分箱/编码/采样)', 'status': 'completed'},
            {'step': 5, 'name': '聚合分析(ADS)', 'source': 'DWD表', 'target': 'ADS聚合表', 'method': 'Hive SQL (GROUP BY/统计)', 'status': 'completed'},
            {'step': 6, 'name': '导出MySQL', 'source': 'Hive ADS表', 'target': 'MySQL heart_disease', 'method': '手动INSERT/Sqoop', 'status': 'completed'},
            {'step': 7, 'name': '模型训练', 'source': 'DWD特征数据', 'target': 'model.joblib', 'method': 'Python sklearn/CatBoost', 'status': 'completed'},
        ]
        return Response({'steps': steps})
