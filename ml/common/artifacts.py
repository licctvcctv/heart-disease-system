from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import joblib


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:  # pragma: no cover - defensive
            return value
    return value


@dataclass(slots=True)
class ModelBundle:
    model: Any
    preprocessor: Any
    feature_columns: list[str]
    target_name: str
    target_positive_label: int
    threshold: float
    feature_defaults: dict[str, Any]
    feature_types: dict[str, list[str]]
    model_name: str
    dataset_name: str
    metrics: dict[str, Any] = field(default_factory=dict)
    feature_importance: list[dict[str, Any]] = field(default_factory=list)
    candidate_metrics: list[dict[str, Any]] = field(default_factory=list)

    def to_metadata(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("model", None)
        data.pop("preprocessor", None)
        return _json_safe(data)


def save_model_bundle(bundle: ModelBundle, output_dir: str | Path) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(bundle, target_dir / "model.joblib")

    (target_dir / "metadata.json").write_text(
        json.dumps(bundle.to_metadata(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (target_dir / "metrics.json").write_text(
        json.dumps(_json_safe(bundle.metrics), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (target_dir / "feature_importance.json").write_text(
        json.dumps(_json_safe(bundle.feature_importance), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (target_dir / "fields.json").write_text(
        json.dumps(
            _json_safe(
                {
                    "feature_columns": bundle.feature_columns,
                    "target_name": bundle.target_name,
                    "target_positive_label": bundle.target_positive_label,
                    "feature_types": bundle.feature_types,
                    "feature_defaults": bundle.feature_defaults,
                }
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return target_dir


def load_model_bundle(model_dir: str | Path) -> ModelBundle:
    target_dir = Path(model_dir)
    bundle = joblib.load(target_dir / "model.joblib")
    if not isinstance(bundle, ModelBundle):
        raise TypeError(f"Loaded object from {target_dir / 'model.joblib'} is not a ModelBundle.")
    return bundle

