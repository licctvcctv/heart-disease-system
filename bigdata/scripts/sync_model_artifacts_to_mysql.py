from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import pymysql


FEATURE_LABELS = {
    "BMI": "体重指数",
    "Smoking": "吸烟",
    "AlcoholDrinking": "饮酒",
    "Stroke": "中风史",
    "PhysicalHealth": "身体不适天数",
    "MentalHealth": "心理不适天数",
    "DiffWalking": "行走困难",
    "Sex": "性别",
    "AgeCategory": "年龄段",
    "Race": "种族",
    "Diabetic": "糖尿病",
    "PhysicalActivity": "身体活动",
    "GenHealth": "总体健康状况",
    "SleepTime": "睡眠时长",
    "Asthma": "哮喘",
    "KidneyDisease": "肾病",
    "SkinCancer": "皮肤癌",
}


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    return default if raw is None or raw.strip() == "" else int(raw)


def normalize_feature(raw_feature: str) -> str:
    name = raw_feature.replace("numeric__", "").replace("categorical__", "")
    for feature in sorted(FEATURE_LABELS, key=len, reverse=True):
        if name == feature or name.startswith(f"{feature}_"):
            return feature
    return name


def execute_schema(mysql_conn: pymysql.connections.Connection, schema_path: Path) -> None:
    sql = schema_path.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in sql.split(";") if statement.strip()]
    with mysql_conn.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
    mysql_conn.commit()


def main() -> None:
    project_dir = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Copy sklearn artifact metrics into MySQL ADS model tables.")
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=project_dir / "bigdata" / "mysql" / "ads_schema.sql")
    parser.add_argument("--dataset", default="kaggle_2020")
    parser.add_argument("--top-features", type=int, default=20)
    parser.add_argument("--mysql-host", default=env("ADS_MYSQL_HOST", "127.0.0.1"))
    parser.add_argument("--mysql-port", type=int, default=int_env("ADS_MYSQL_PORT", 3306))
    parser.add_argument("--mysql-user", default=env("ADS_MYSQL_USER", "heart_user"))
    parser.add_argument("--mysql-password", default=env("ADS_MYSQL_PASSWORD", "heart_password"))
    parser.add_argument("--mysql-database", default=env("ADS_MYSQL_DATABASE", "heart_disease"))
    args = parser.parse_args()

    metrics = json.loads((args.model_dir / "metrics.json").read_text(encoding="utf-8"))
    importance = json.loads((args.model_dir / "feature_importance.json").read_text(encoding="utf-8"))
    selected_model = metrics.get("selected_model", "model")

    model_rows = [
        (
            row.get("name", "model"),
            row.get("accuracy", 0.0),
            row.get("precision", 0.0),
            row.get("recall", 0.0),
            row.get("f1", 0.0),
            row.get("roc_auc", row.get("auc", 0.0)),
            args.dataset,
            "selected" if row.get("name") == selected_model else "candidate",
        )
        for row in metrics.get("candidate_metrics", [])
    ]

    feature_rows = []
    for row in importance[: args.top_features]:
        feature = normalize_feature(str(row.get("feature", "")))
        feature_rows.append(
            (
                selected_model,
                feature,
                FEATURE_LABELS.get(feature, feature),
                row.get("importance", 0.0),
                args.dataset,
            )
        )

    mysql_conn = pymysql.connect(
        host=args.mysql_host,
        port=args.mysql_port,
        user=args.mysql_user,
        password=args.mysql_password,
        database=args.mysql_database,
        charset="utf8mb4",
        autocommit=False,
    )
    try:
        execute_schema(mysql_conn, args.schema)
        with mysql_conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE ads_model_metrics")
            cursor.executemany(
                """
                INSERT INTO ads_model_metrics
                    (model_name, accuracy, precision_score, recall_score, f1_score, auc, train_dataset, note, load_dt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE())
                """,
                model_rows,
            )
            cursor.execute("TRUNCATE TABLE ads_model_feature_importance")
            cursor.executemany(
                """
                INSERT INTO ads_model_feature_importance
                    (model_name, feature_name, feature_label, importance, train_dataset, load_dt)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE())
                """,
                feature_rows,
            )
        mysql_conn.commit()
        print(f"ads_model_metrics: {len(model_rows)} rows")
        print(f"ads_model_feature_importance: {len(feature_rows)} rows")
    finally:
        mysql_conn.close()


if __name__ == "__main__":
    main()
