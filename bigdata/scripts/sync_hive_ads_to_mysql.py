from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import pymysql
from pyhive import hive


ADS_TABLES: dict[str, list[str]] = {
    "ads_heart_overview": [
        "dataset_name",
        "sample_count",
        "positive_count",
        "negative_count",
        "prevalence_rate",
        "source_file",
        "load_dt",
    ],
    "ads_heart_by_age": ["dataset_name", "age_band", "sample_count", "positive_count", "prevalence_rate", "load_dt"],
    "ads_heart_by_sex": [
        "dataset_name",
        "sex_code",
        "sex_label",
        "sample_count",
        "positive_count",
        "prevalence_rate",
        "load_dt",
    ],
    "ads_heart_by_bmi": ["dataset_name", "bmi_group", "sample_count", "positive_count", "prevalence_rate", "load_dt"],
    "ads_heart_lifestyle": [
        "dataset_name",
        "factor_name",
        "factor_value",
        "sample_count",
        "positive_count",
        "prevalence_rate",
        "load_dt",
    ],
    "ads_heart_comorbidity": [
        "dataset_name",
        "disease_name",
        "disease_flag",
        "sample_count",
        "positive_count",
        "prevalence_rate",
        "load_dt",
    ],
    "ads_uci_clinical_risk": [
        "feature_name",
        "feature_label",
        "feature_value",
        "sample_count",
        "positive_count",
        "prevalence_rate",
        "load_dt",
    ],
    "ads_uci_cost_analysis": ["feature", "cost", "cost_rank", "cost_level", "load_dt"],
    "ads_model_metrics": [
        "model_name",
        "accuracy",
        "precision_score",
        "recall_score",
        "f1_score",
        "auc",
        "train_dataset",
        "note",
        "load_dt",
    ],
    "ads_model_feature_importance": [
        "model_name",
        "feature_name",
        "feature_label",
        "importance",
        "train_dataset",
        "load_dt",
    ],
}


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    return default if raw is None or raw.strip() == "" else int(raw)


def execute_schema(mysql_conn: pymysql.connections.Connection, schema_path: Path) -> None:
    sql = schema_path.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in sql.split(";") if statement.strip()]
    with mysql_conn.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
    mysql_conn.commit()


def fetch_hive_rows(hive_conn: hive.Connection, table: str, columns: list[str]) -> list[tuple[Any, ...]]:
    sql = f"SELECT {', '.join(columns)} FROM {table}"
    cursor = hive_conn.cursor()
    try:
        cursor.execute(sql)
        return list(cursor.fetchall())
    finally:
        cursor.close()


def replace_mysql_rows(mysql_conn: pymysql.connections.Connection, table: str, columns: list[str], rows: list[tuple[Any, ...]]) -> None:
    placeholders = ", ".join(["%s"] * len(columns))
    column_sql = ", ".join(columns)
    insert_sql = f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})"
    with mysql_conn.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table}")
        if rows:
            cursor.executemany(insert_sql, rows)
    mysql_conn.commit()


def main() -> None:
    project_dir = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Copy offline Hive ADS tables into MySQL for Django API reads.")
    parser.add_argument("--schema", type=Path, default=project_dir / "bigdata" / "mysql" / "ads_schema.sql")
    parser.add_argument("--hive-host", default=env("HIVE_HOST", "127.0.0.1"))
    parser.add_argument("--hive-port", type=int, default=int_env("HIVE_PORT", 10000))
    parser.add_argument("--hive-user", default=env("HIVE_USER", env("USER", "root1")))
    parser.add_argument("--hive-auth", default=env("HIVE_AUTH", "NONE"))
    parser.add_argument("--hive-database", default=env("HIVE_DATABASE", "heart_disease_system"))
    parser.add_argument("--mysql-host", default=env("ADS_MYSQL_HOST", "127.0.0.1"))
    parser.add_argument("--mysql-port", type=int, default=int_env("ADS_MYSQL_PORT", 3306))
    parser.add_argument("--mysql-user", default=env("ADS_MYSQL_USER", "heart_user"))
    parser.add_argument("--mysql-password", default=env("ADS_MYSQL_PASSWORD", "heart_password"))
    parser.add_argument("--mysql-database", default=env("ADS_MYSQL_DATABASE", "heart_disease"))
    args = parser.parse_args()

    hive_conn = hive.connect(
        host=args.hive_host,
        port=args.hive_port,
        username=args.hive_user,
        database=args.hive_database,
        auth=args.hive_auth,
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
        for table, columns in ADS_TABLES.items():
            rows = fetch_hive_rows(hive_conn, table, columns)
            replace_mysql_rows(mysql_conn, table, columns, rows)
            print(f"{table}: {len(rows)} rows")
    finally:
        mysql_conn.close()
        hive_conn.close()


if __name__ == "__main__":
    main()
