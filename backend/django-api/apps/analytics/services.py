from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from django.utils import timezone

from .repositories import AdsQueryClient, DataUnavailable


AGE_ORDER = [
    "18-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70-74",
    "75-79",
    "80 or older",
    "Under 40",
    "40-49",
    "50-59",
    "60-69",
    "70+",
]

DATASET_META = {
    "kaggle_2020": {
        "name": "Kaggle 2020 BRFSS",
        "columns": 18,
        "target": "HeartDisease",
        "usage": "主分析与模型训练",
    },
    "kaggle_2022": {
        "name": "Kaggle 2022 BRFSS",
        "columns": 40,
        "target": "HadHeartAttack/HadAngina",
        "usage": "扩展分析与缺失值清洗展示",
    },
    "uci_cleveland": {
        "name": "UCI Cleveland",
        "columns": 14,
        "target": "num",
        "usage": "临床指标分析与辅助预测",
    },
}

LIFESTYLE_FACTOR_MAP = {
    "smoking_flag": "Smoking",
    "alcohol_flag": "AlcoholDrinking",
    "activity_flag": "PhysicalActivity",
    "sleep_metric": "SleepTime",
}

COMORBIDITY_FACTOR_MAP = {
    "stroke": "Stroke",
    "diabetes": "Diabetic",
    "kidney_disease": "KidneyDisease",
    "asthma": "Asthma",
    "skin_cancer": "SkinCancer",
}

CLINICAL_VALUE_LABELS = {
    "cp": {
        "1": "typical angina",
        "2": "atypical angina",
        "3": "non-anginal pain",
        "4": "asymptomatic",
    },
    "sex_code": {"0": "Female", "1": "Male"},
    "exang": {"0": "No", "1": "Yes"},
    "thal": {"3": "normal", "6": "fixed defect", "7": "reversible defect"},
}

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


def _client() -> AdsQueryClient:
    return AdsQueryClient()


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    return int(float(value))


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _rate(positive_count: int, sample_count: int) -> float:
    return 0.0 if sample_count <= 0 else round(positive_count / sample_count, 4)


def _binary_label(value: Any) -> str:
    text = str(value).strip()
    if text in {"1", "1.0", "true", "True", "yes", "Yes"}:
        return "Yes"
    if text in {"0", "0.0", "false", "False", "no", "No"}:
        return "No"
    return text or "Unknown"


def _sort_age_key(item: dict[str, Any]) -> int:
    age_group = item["ageGroup"]
    return AGE_ORDER.index(age_group) if age_group in AGE_ORDER else 999


def _add_group(groups: dict[str, dict[str, int]], key: str, sample_count: Any, positive_count: Any) -> None:
    groups[key]["sampleCount"] += _to_int(sample_count)
    groups[key]["positiveCount"] += _to_int(positive_count)


def _metric_items(groups: dict[str, dict[str, int]], output_name: str) -> list[dict[str, Any]]:
    items = []
    for key, values in groups.items():
        sample_count = values["sampleCount"]
        positive_count = values["positiveCount"]
        items.append(
            {
                output_name: key,
                "sampleCount": sample_count,
                "positiveCount": positive_count,
                "prevalenceRate": _rate(positive_count, sample_count),
            }
        )
    return items


def _factor_item(factor: str, category: str, sample_count: Any, positive_count: Any) -> dict[str, Any]:
    sample = _to_int(sample_count)
    positive = _to_int(positive_count)
    return {
        "factor": factor,
        "category": category,
        "sampleCount": sample,
        "positiveCount": positive,
        "prevalenceRate": _rate(positive, sample),
    }


def _ensure_rows(rows: list[dict[str, Any]], table_name: str) -> list[dict[str, Any]]:
    if not rows:
        raise DataUnavailable(f"ADS 表 {table_name} 暂无数据，请先执行 Hive 建仓并同步到 MySQL。")
    return rows


class OverviewService:
    @staticmethod
    def get_data() -> dict[str, Any]:
        rows = _ensure_rows(
            _client().fetch_all(
                """
                SELECT dataset_name, sample_count, positive_count, negative_count,
                       prevalence_rate, source_file, load_dt
                FROM ads_heart_overview
                """
            ),
            "ads_heart_overview",
        )

        sample_count = sum(_to_int(row.get("sample_count")) for row in rows)
        positive_count = sum(_to_int(row.get("positive_count")) for row in rows)
        negative_count = sum(_to_int(row.get("negative_count")) for row in rows)
        metrics = ModelMetricsService.get_data()
        model_auc = max((item["auc"] for item in metrics["models"]), default=0.0)

        datasets = []
        for row in rows:
            dataset_key = str(row.get("dataset_name", "")).strip()
            meta = DATASET_META.get(dataset_key.lower(), {})
            datasets.append(
                {
                    "name": meta.get("name", dataset_key),
                    "rows": _to_int(row.get("sample_count")),
                    "columns": meta.get("columns", 0),
                    "target": meta.get("target", "risk_label"),
                    "usage": meta.get("usage", "ADS 指标分析"),
                    "positiveCount": _to_int(row.get("positive_count")),
                    "prevalenceRate": _rate(_to_int(row.get("positive_count")), _to_int(row.get("sample_count"))),
                }
            )

        return {
            "sampleCount": sample_count,
            "positiveCount": positive_count,
            "negativeCount": negative_count,
            "prevalenceRate": _rate(positive_count, sample_count),
            "datasetCount": len(datasets),
            "modelAuc": round(float(model_auc), 4),
            "updatedAt": timezone.localtime(timezone.now()).isoformat(),
            "datasets": datasets,
        }


class AnalysisService:
    @staticmethod
    def age_data() -> dict[str, Any]:
        rows = _ensure_rows(
            _client().fetch_all(
                """
                SELECT age_band, sample_count, positive_count
                FROM ads_heart_by_age
                WHERE age_band IS NOT NULL AND trim(age_band) <> ''
                """
            ),
            "ads_heart_by_age",
        )
        groups: dict[str, dict[str, int]] = defaultdict(lambda: {"sampleCount": 0, "positiveCount": 0})
        for row in rows:
            _add_group(groups, str(row.get("age_band", "Unknown")), row.get("sample_count"), row.get("positive_count"))
        items = _metric_items(groups, "ageGroup")
        items.sort(key=_sort_age_key)
        return {"items": items}

    @staticmethod
    def lifestyle_data() -> dict[str, Any]:
        items: list[dict[str, Any]] = []

        lifestyle_rows = _client().fetch_all(
            """
            SELECT factor_name, factor_value, sample_count, positive_count
            FROM ads_heart_lifestyle
            """
        )
        for row in lifestyle_rows:
            factor = LIFESTYLE_FACTOR_MAP.get(str(row.get("factor_name", "")).strip())
            if not factor:
                continue
            value = row.get("factor_value")
            category = str(value).strip() if factor == "SleepTime" else _binary_label(value)
            items.append(_factor_item(factor, category, row.get("sample_count"), row.get("positive_count")))

        sex_rows = _client().fetch_all(
            """
            SELECT sex_label, sample_count, positive_count
            FROM ads_heart_by_sex
            """
        )
        for row in sex_rows:
            items.append(_factor_item("Sex", str(row.get("sex_label", "Unknown")), row.get("sample_count"), row.get("positive_count")))

        bmi_rows = _client().fetch_all(
            """
            SELECT bmi_group, sample_count, positive_count
            FROM ads_heart_by_bmi
            """
        )
        for row in bmi_rows:
            items.append(_factor_item("BMI", str(row.get("bmi_group", "Unknown")), row.get("sample_count"), row.get("positive_count")))

        comorbidity_rows = _client().fetch_all(
            """
            SELECT disease_name, disease_flag, sample_count, positive_count
            FROM ads_heart_comorbidity
            """
        )
        for row in comorbidity_rows:
            factor = COMORBIDITY_FACTOR_MAP.get(str(row.get("disease_name", "")).strip())
            if factor:
                items.append(_factor_item(factor, _binary_label(row.get("disease_flag")), row.get("sample_count"), row.get("positive_count")))

        if not items:
            raise DataUnavailable("ADS 生活方式与共病指标暂无数据，请先执行 Hive 建仓并同步到 MySQL。")
        return {"items": items}

    @staticmethod
    def clinical_data() -> dict[str, Any]:
        rows = _ensure_rows(
            _client().fetch_all(
                """
                SELECT feature_name, feature_label, feature_value, sample_count, positive_count
                FROM ads_uci_clinical_risk
                """
            ),
            "ads_uci_clinical_risk",
        )

        grouped: dict[str, dict[str, Any]] = {}
        for row in rows:
            feature = str(row.get("feature_name", "")).strip()
            label = str(row.get("feature_label", feature)).strip()
            value = str(row.get("feature_value", "Unknown")).strip()
            value_label = CLINICAL_VALUE_LABELS.get(feature, {}).get(value, value)
            sample_count = _to_int(row.get("sample_count"))
            positive_count = _to_int(row.get("positive_count"))
            grouped.setdefault(feature, {"feature": feature, "label": label, "groups": []})
            grouped[feature]["groups"].append(
                {
                    "category": value_label,
                    "sampleCount": sample_count,
                    "positiveCount": positive_count,
                    "prevalenceRate": _rate(positive_count, sample_count),
                }
            )

        return {"items": list(grouped.values())}


class ModelMetricsService:
    @staticmethod
    def get_data() -> dict[str, Any]:
        model_rows = _ensure_rows(
            _client().fetch_all(
                """
                SELECT model_name, accuracy, precision_score, recall_score, f1_score, auc
                FROM ads_model_metrics
                ORDER BY auc DESC
                """
            ),
            "ads_model_metrics",
        )
        feature_rows = _ensure_rows(
            _client().fetch_all(
                """
                SELECT feature_name, feature_label, importance
                FROM ads_model_feature_importance
                ORDER BY importance DESC
                LIMIT 8
                """
            ),
            "ads_model_feature_importance",
        )

        models = [
            {
                "name": str(row.get("model_name", "model")).replace("_", " ").title(),
                "accuracy": round(_to_float(row.get("accuracy")), 4),
                "precision": round(_to_float(row.get("precision_score")), 4),
                "recall": round(_to_float(row.get("recall_score")), 4),
                "f1": round(_to_float(row.get("f1_score")), 4),
                "auc": round(_to_float(row.get("auc")), 4),
            }
            for row in model_rows
        ]
        feature_importance = [
            {
                "feature": str(row.get("feature_name", "")),
                "label": str(row.get("feature_label") or FEATURE_LABELS.get(str(row.get("feature_name", "")), row.get("feature_name", ""))),
                "importance": round(_to_float(row.get("importance")), 4),
            }
            for row in feature_rows
        ]
        return {"models": models, "featureImportance": feature_importance}
