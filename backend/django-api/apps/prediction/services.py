from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from django.utils import timezone
from rest_framework.exceptions import APIException


def _risk_level(probability: float) -> tuple[str, str]:
    if probability >= 0.67:
        return "high", "高风险"
    if probability >= 0.33:
        return "medium", "中风险"
    return "low", "低风险"


class ModelUnavailable(APIException):
    status_code = 503
    default_detail = "No trained model artifact is available. Train a model before calling /api/predict."
    default_code = "model_unavailable"


class PredictionService:
    _model_bundle = None

    @staticmethod
    def _project_root() -> Path:
        return Path(__file__).resolve().parents[4]

    @classmethod
    def _load_model_bundle(cls):
        if cls._model_bundle is not None:
            return cls._model_bundle

        project_root = cls._project_root()
        ml_root = project_root / "ml"
        model_dir = Path(os.getenv("ML_MODEL_DIR", project_root / "ml" / "artifacts" / "smoke" / "kaggle_2020"))
        if str(ml_root) not in sys.path:
            sys.path.insert(0, str(ml_root))

        try:
            from predict.predict import load_model_bundle
        except Exception:
            return None

        try:
            cls._model_bundle = load_model_bundle(model_dir)
        except Exception:
            return None
        return cls._model_bundle

    @staticmethod
    def _from_ml_result(payload: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        probability = float(result.get("probability", 0.0))
        risk_level, risk_label = _risk_level(probability)
        return {
            "probability": round(probability, 4),
            "riskLevel": risk_level,
            "riskLabel": risk_label,
            "model": str(result.get("model_name", "sklearn_model")).replace("_", " ").title(),
            "topFactors": [
                {"feature": "AgeCategory", "label": "年龄段", "impact": str(payload.get("AgeCategory", "unknown"))},
                {"feature": "Smoking", "label": "吸烟", "impact": str(payload.get("Smoking", "unknown"))},
                {"feature": "GenHealth", "label": "总体健康状况", "impact": str(payload.get("GenHealth", "unknown"))},
            ],
            "createdAt": timezone.localtime(timezone.now()).isoformat(),
        }

    @classmethod
    def predict(cls, payload: dict[str, Any]) -> dict[str, Any]:
        bundle = cls._load_model_bundle()
        if bundle is None:
            raise ModelUnavailable()

        from predict.predict import predict_single

        result = predict_single(payload, model_bundle=bundle)
        if not isinstance(result, dict):
            raise ModelUnavailable("Model returned an invalid result.")
        return cls._from_ml_result(payload, result)
