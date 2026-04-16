from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


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


def sql_quote(value: Any) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def normalize_feature(raw_feature: str) -> str:
    name = raw_feature.replace("numeric__", "").replace("categorical__", "")
    for feature in sorted(FEATURE_LABELS, key=len, reverse=True):
        if name == feature or name.startswith(f"{feature}_"):
            return feature
    return name


def decimal_expr(value: Any, precision: str = "8,4") -> str:
    return f"CAST({float(value):.8f} AS DECIMAL({precision}))"


def union_insert(table: str, selects: list[str]) -> str:
    if not selects:
        raise ValueError(f"No rows generated for {table}")
    return f"INSERT OVERWRITE TABLE {table}\n" + "\nUNION ALL\n".join(selects) + ";\n"


def build_sql(model_dir: Path, dataset: str, top_features: int) -> str:
    metrics = json.loads((model_dir / "metrics.json").read_text(encoding="utf-8"))
    importance = json.loads((model_dir / "feature_importance.json").read_text(encoding="utf-8"))

    model_selects = []
    for row in metrics.get("candidate_metrics", []):
        model_selects.append(
            "SELECT "
            f"{sql_quote(row.get('name', 'model'))} AS model_name, "
            f"{decimal_expr(row.get('accuracy', 0.0))} AS accuracy, "
            f"{decimal_expr(row.get('precision', 0.0))} AS precision_score, "
            f"{decimal_expr(row.get('recall', 0.0))} AS recall_score, "
            f"{decimal_expr(row.get('f1', 0.0))} AS f1_score, "
            f"{decimal_expr(row.get('roc_auc', row.get('auc', 0.0)))} AS auc, "
            f"{sql_quote(dataset)} AS train_dataset, "
            f"{sql_quote('selected' if row.get('name') == metrics.get('selected_model') else 'candidate')} AS note, "
            "date_format(current_date(), 'yyyy-MM-dd') AS load_dt"
        )

    feature_selects = []
    selected_model = metrics.get("selected_model", "model")
    for row in importance[:top_features]:
        feature = normalize_feature(str(row.get("feature", "")))
        feature_selects.append(
            "SELECT "
            f"{sql_quote(selected_model)} AS model_name, "
            f"{sql_quote(feature)} AS feature_name, "
            f"{sql_quote(FEATURE_LABELS.get(feature, feature))} AS feature_label, "
            f"{decimal_expr(row.get('importance', 0.0), '12,6')} AS importance, "
            f"{sql_quote(dataset)} AS train_dataset, "
            "date_format(current_date(), 'yyyy-MM-dd') AS load_dt"
        )

    return (
        "USE ${hiveconf:hive_database};\n"
        + union_insert("ads_model_metrics", model_selects)
        + "\n"
        + union_insert("ads_model_feature_importance", feature_selects)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync sklearn artifact metrics into Hive ADS model tables.")
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--dataset", default="kaggle_2020")
    parser.add_argument("--top-features", type=int, default=20)
    parser.add_argument("--hive-database", default="heart_disease_system")
    parser.add_argument("--hive-replication", default="1")
    parser.add_argument("--sql-out", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    sql = build_sql(args.model_dir, args.dataset, args.top_features)
    sql_path = args.sql_out
    if sql_path is None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8")
        sql_path = Path(tmp.name)
        tmp.write(sql)
        tmp.close()
    else:
        sql_path.write_text(sql, encoding="utf-8")

    print(sql_path)
    if args.execute:
        subprocess.run(
            [
                "hive",
                "--hiveconf",
                f"hive_database={args.hive_database}",
                "--hiveconf",
                f"dfs.replication={args.hive_replication}",
                "-f",
                str(sql_path),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
