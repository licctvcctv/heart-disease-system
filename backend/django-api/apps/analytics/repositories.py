from __future__ import annotations

import os
from typing import Any

from rest_framework.exceptions import APIException


class DataUnavailable(APIException):
    status_code = 503
    default_detail = "ADS analysis data is unavailable."
    default_code = "data_unavailable"


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _column_name(raw: Any) -> str:
    name = str(raw).split(".")[-1]
    return name.strip().lower()


class AdsQueryClient:
    """Small DB-API wrapper for querying offline MySQL ADS tables or Hive during maintenance."""

    def __init__(self) -> None:
        self.engine = os.getenv("ANALYTICS_QUERY_ENGINE", "mysql").strip().lower()

    def fetch_all(self, sql: str) -> list[dict[str, Any]]:
        if self.engine == "mysql":
            return self._fetch_mysql(sql)
        if self.engine == "hive":
            return self._fetch_hive(sql)
        raise DataUnavailable(f"不支持的 ANALYTICS_QUERY_ENGINE：{self.engine}")

    def _fetch_hive(self, sql: str) -> list[dict[str, Any]]:
        try:
            from pyhive import hive
        except ImportError as exc:
            raise DataUnavailable("缺少 PyHive 依赖，无法连接 Hive ADS 表。请先安装 requirements.txt。") from exc

        try:
            connection = hive.connect(
                host=os.getenv("HIVE_HOST", "127.0.0.1"),
                port=_int_env("HIVE_PORT", 10000),
                username=os.getenv("HIVE_USER", os.getenv("USER", "root1")),
                database=os.getenv("HIVE_DATABASE", "heart_disease_system"),
                auth=os.getenv("HIVE_AUTH", "NONE"),
            )
            try:
                cursor = connection.cursor()
                try:
                    cursor.execute(sql)
                    columns = [_column_name(item[0]) for item in cursor.description or []]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                finally:
                    cursor.close()
            finally:
                connection.close()
        except DataUnavailable:
            raise
        except Exception as exc:
            raise DataUnavailable(f"Hive ADS 查询失败：{exc}") from exc

    def _fetch_mysql(self, sql: str) -> list[dict[str, Any]]:
        try:
            import pymysql
        except ImportError as exc:
            raise DataUnavailable("缺少 PyMySQL 依赖，无法连接 MySQL ADS 表。请先安装 requirements.txt。") from exc

        try:
            connection = pymysql.connect(
                host=os.getenv("ADS_MYSQL_HOST", os.getenv("DATABASE_HOST", "127.0.0.1")),
                port=_int_env("ADS_MYSQL_PORT", _int_env("DATABASE_PORT", 3306)),
                user=os.getenv("ADS_MYSQL_USER", os.getenv("DATABASE_USER", "root")),
                password=os.getenv("ADS_MYSQL_PASSWORD", os.getenv("DATABASE_PASSWORD", "")),
                database=os.getenv("ADS_MYSQL_DATABASE", os.getenv("DATABASE_NAME", "heart_disease")),
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    return [{_column_name(key): value for key, value in row.items()} for row in cursor.fetchall()]
            finally:
                connection.close()
        except DataUnavailable:
            raise
        except Exception as exc:
            raise DataUnavailable(f"MySQL ADS 查询失败：{exc}。请先把 Hive ADS 离线同步到 MySQL。") from exc
