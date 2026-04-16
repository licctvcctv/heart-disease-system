from __future__ import annotations

import os
import subprocess

import pymysql
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PredictionRecord


class WarehouseView(APIView):
    """GET /api/system/warehouse  -- list tables and row counts from MySQL."""

    def get(self, request):
        conn = pymysql.connect(
            host=os.getenv("ADS_MYSQL_HOST", "127.0.0.1"),
            port=int(os.getenv("ADS_MYSQL_PORT", "3306")),
            user=os.getenv("ADS_MYSQL_USER", "heart_user"),
            password=os.getenv("ADS_MYSQL_PASSWORD", "heart_password"),
            database="information_schema",
            charset="utf8mb4",
        )
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT table_name, table_rows "
                    "FROM tables "
                    "WHERE table_schema = %s "
                    "ORDER BY table_name",
                    ("heart_disease",),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        layers = {"ods": [], "dwd": [], "ads": [], "other": []}
        for name, cnt in rows:
            entry = {"name": name, "rows": cnt or 0}
            lower = name.lower()
            if lower.startswith("ods_"):
                entry["description"] = "原始数据"
                layers["ods"].append(entry)
            elif lower.startswith("dwd_"):
                entry["description"] = "明细数据"
                layers["dwd"].append(entry)
            elif lower.startswith("ads_"):
                entry["description"] = "应用数据"
                layers["ads"].append(entry)
            else:
                entry["description"] = "其他表"
                layers["other"].append(entry)

        # Remove empty buckets
        layers = {k: v for k, v in layers.items() if v}
        return Response({"layers": layers})


class ClusterStatusView(APIView):
    """GET /api/system/cluster  -- report running services."""

    SERVICE_PORT_MAP = [
        ("HDFS NameNode", 9870),
        ("YARN ResourceManager", 8088),
        ("Hive Server2", 10000),
        ("MySQL", 3306),
        ("Django API", 8000),
    ]

    def get(self, request):
        # --- Java processes via jps ---
        try:
            jps_out = subprocess.check_output(
                ["jps"], stderr=subprocess.STDOUT, timeout=5
            ).decode()
            java_procs = [
                line.split(None, 1)[1]
                for line in jps_out.strip().splitlines()
                if len(line.split(None, 1)) == 2 and line.split(None, 1)[1] != "Jps"
            ]
        except Exception:
            java_procs = []

        # --- Port check via ss ---
        try:
            ss_out = subprocess.check_output(
                ["ss", "-tlnp"], stderr=subprocess.STDOUT, timeout=5
            ).decode()
        except Exception:
            ss_out = ""

        services = []
        for svc_name, port in self.SERVICE_PORT_MAP:
            listening = f":{port}" in ss_out
            services.append(
                {
                    "name": svc_name,
                    "status": "running" if listening else "stopped",
                    "port": port,
                }
            )

        return Response({"services": services, "javaProcesses": java_procs})


class PredictionHistoryView(APIView):
    """GET /api/system/predictions  -- recent 50 prediction records."""

    def get(self, request):
        qs = PredictionRecord.objects.order_by("-created_at")[:50]
        data = [
            {
                "id": r.id,
                "probability": r.probability,
                "riskLevel": r.risk_level,
                "riskLabel": r.risk_label,
                "modelName": r.model_name,
                "inputData": r.input_data,
                "createdAt": r.created_at.isoformat(),
            }
            for r in qs
        ]
        return Response({"records": data, "total": len(data)})


class ETLStepsView(APIView):
    """GET /api/system/etl-steps  -- static ETL pipeline description."""

    def get(self, request):
        steps = [
            {
                "step": 1,
                "name": "CSV导入HDFS",
                "source": "本地CSV",
                "target": "HDFS /user/hive/warehouse",
                "method": "hdfs dfs -put",
                "status": "completed",
            },
            {
                "step": 2,
                "name": "ODS层建表",
                "source": "HDFS",
                "target": "Hive ODS表",
                "method": "Hive CREATE EXTERNAL TABLE",
                "status": "completed",
            },
            {
                "step": 3,
                "name": "数据清洗",
                "source": "ODS层",
                "target": "DWD层",
                "method": "Hive SQL 去重/缺失值处理",
                "status": "completed",
            },
            {
                "step": 4,
                "name": "聚合分析",
                "source": "DWD层",
                "target": "ADS层",
                "method": "Hive SQL 分组聚合",
                "status": "completed",
            },
            {
                "step": 5,
                "name": "导出MySQL",
                "source": "Hive ADS",
                "target": "MySQL heart_disease",
                "method": "Sqoop/手动导出",
                "status": "completed",
            },
            {
                "step": 6,
                "name": "模型训练",
                "source": "DWD层数据",
                "target": "model.joblib",
                "method": "Python sklearn/catboost",
                "status": "completed",
            },
        ]
        return Response({"steps": steps})
