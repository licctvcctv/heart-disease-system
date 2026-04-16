from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ML_ROOT = Path(__file__).resolve().parents[1]
if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from common.artifacts import ModelBundle, load_model_bundle as _load_model_bundle
from common.preprocessing import coerce_input_payload
from common.training import predict_bundle


def load_model_bundle(model_dir: str | Path) -> ModelBundle:
    return _load_model_bundle(model_dir)


def predict_batch(
    payload: list[dict[str, Any]] | dict[str, Any] | Any,
    *,
    model_bundle: ModelBundle | None = None,
    model_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    if model_bundle is None and model_dir is None:
        raise ValueError("model_bundle or model_dir must be provided.")
    bundle = model_bundle or _load_model_bundle(model_dir)
    return predict_bundle(payload, bundle)


def predict_single(
    payload: dict[str, Any] | Any,
    *,
    model_bundle: ModelBundle | None = None,
    model_dir: str | Path | None = None,
) -> dict[str, Any]:
    result = predict_batch(payload, model_bundle=model_bundle, model_dir=model_dir)
    return result[0]
