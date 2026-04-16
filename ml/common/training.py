from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

try:  # optional dependency
    from xgboost import XGBClassifier  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    XGBClassifier = None  # type: ignore

try:  # optional dependency
    from catboost import CatBoostClassifier  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    CatBoostClassifier = None  # type: ignore

from .artifacts import ModelBundle, save_model_bundle
from .preprocessing import (
    DatasetBundle,
    build_feature_defaults,
    build_preprocessor,
    coerce_input_payload,
)


@dataclass(slots=True)
class TrainedCandidate:
    name: str
    model: Any
    metrics: dict[str, Any]


def _safe_probability_scores(model: Any, X: Any) -> np.ndarray:
    if model.__class__.__name__ == "LogisticRegression" and not hasattr(model, "multi_class"):
        # scikit-learn 1.8 model artifacts no longer persist this attribute, but
        # 1.7.x still reads it in predict_proba().
        model.multi_class = "auto"
    if hasattr(model, "predict_proba"):
        scores = model.predict_proba(X)
        return scores[:, 1] if scores.ndim == 2 and scores.shape[1] > 1 else scores.ravel()
    if hasattr(model, "decision_function"):
        decision = model.decision_function(X)
        return 1.0 / (1.0 + np.exp(-np.asarray(decision)))
    predictions = model.predict(X)
    return np.asarray(predictions, dtype=float)


def _evaluate_candidate(model: Any, X_valid: Any, y_valid: pd.Series) -> dict[str, Any]:
    probability = _safe_probability_scores(model, X_valid)
    predictions = (probability >= 0.5).astype(int)
    metrics = {
        "accuracy": float(accuracy_score(y_valid, predictions)),
        "precision": float(precision_score(y_valid, predictions, zero_division=0)),
        "recall": float(recall_score(y_valid, predictions, zero_division=0)),
        "f1": float(f1_score(y_valid, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_valid, probability)) if len(set(y_valid)) > 1 else 0.0,
        "log_loss": float(log_loss(y_valid, np.clip(probability, 1e-6, 1 - 1e-6))),
    }
    return metrics


def _candidate_factories(random_state: int) -> dict[str, Callable[[], Any]]:
    candidates: dict[str, Callable[[], Any]] = {
        "sgd_logistic": lambda: SGDClassifier(
            loss="log_loss",
            alpha=1e-4,
            max_iter=2000,
            tol=1e-3,
            class_weight="balanced",
            random_state=random_state,
        ),
        "logistic_regression": lambda: LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs",
        ),
        "random_forest": lambda: RandomForestClassifier(
            n_estimators=250,
            random_state=random_state,
            class_weight="balanced_subsample",
            n_jobs=-1,
        ),
        "extra_trees": lambda: ExtraTreesClassifier(
            n_estimators=300,
            random_state=random_state,
            class_weight="balanced",
            n_jobs=-1,
        ),
    }
    if XGBClassifier is not None:
        candidates["xgboost"] = lambda: XGBClassifier(
            n_estimators=250,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.85,
            colsample_bytree=0.85,
            eval_metric="logloss",
            tree_method="hist",
            random_state=random_state,
        )
    if CatBoostClassifier is not None:
        candidates["catboost"] = lambda: CatBoostClassifier(
            iterations=300,
            learning_rate=0.05,
            depth=6,
            loss_function="Logloss",
            verbose=False,
            random_seed=random_state,
        )
    return candidates


def _feature_importance(
    preprocessor: Any,
    estimator: Any,
    feature_columns: list[str],
) -> list[dict[str, Any]]:
    transformed_names = list(preprocessor.get_feature_names_out(feature_columns))
    importance_values: np.ndarray | None = None
    coefficient_values: np.ndarray | None = None

    if hasattr(estimator, "feature_importances_"):
        importance_values = np.asarray(estimator.feature_importances_, dtype=float)
    elif hasattr(estimator, "coef_"):
        coef = np.asarray(estimator.coef_, dtype=float)
        coefficient_values = coef[0] if coef.ndim > 1 else coef.ravel()
        importance_values = np.abs(coefficient_values)

    if importance_values is None:
        return []

    rows: list[dict[str, Any]] = []
    for index, name in enumerate(transformed_names):
        row: dict[str, Any] = {
            "feature": name,
            "importance": float(importance_values[index]),
        }
        if coefficient_values is not None:
            row["coefficient"] = float(coefficient_values[index])
        rows.append(row)
    rows.sort(key=lambda item: item["importance"], reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows


def train_classification_bundle(
    dataset: DatasetBundle,
    *,
    output_dir: str | Path | None = None,
    model_name: str = "auto",
    test_size: float = 0.2,
    random_state: int = 42,
    sample_size: int | None = None,
) -> tuple[ModelBundle, dict[str, Any]]:
    X = dataset.X.copy()
    y = dataset.y.copy()

    if sample_size is not None and len(X) > sample_size:
        X, _, y, _ = train_test_split(
            X,
            y,
            train_size=int(sample_size),
            random_state=random_state,
            stratify=y,
        )

    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    preprocessor = build_preprocessor(
        X_train,
        numeric_columns=dataset.numeric_columns,
        categorical_columns=dataset.categorical_columns,
    )
    X_train_encoded = preprocessor.fit_transform(X_train)
    X_valid_encoded = preprocessor.transform(X_valid)

    available_factories = _candidate_factories(random_state)
    if model_name == "auto":
        candidate_names = ["sgd_logistic", "logistic_regression"]
        if len(X_train) <= 50000:
            candidate_names.extend(["random_forest", "extra_trees"])
    else:
        candidate_names = [model_name]

    candidate_results: list[TrainedCandidate] = []
    for candidate_name in candidate_names:
        if candidate_name not in available_factories:
            continue
        estimator = available_factories[candidate_name]()
        estimator.fit(X_train_encoded, y_train)
        metrics = _evaluate_candidate(estimator, X_valid_encoded, y_valid)
        candidate_results.append(TrainedCandidate(candidate_name, estimator, metrics))

    if not candidate_results:
        raise RuntimeError("No candidate models were trained successfully.")

    candidate_results.sort(
        key=lambda item: (
            item.metrics.get("roc_auc", 0.0),
            item.metrics.get("f1", 0.0),
            item.metrics.get("accuracy", 0.0),
        ),
        reverse=True,
    )
    winner = candidate_results[0]
    feature_defaults = build_feature_defaults(
        X_train,
        numeric_columns=dataset.numeric_columns,
        categorical_columns=dataset.categorical_columns,
    )
    bundle = ModelBundle(
        model=winner.model,
        preprocessor=preprocessor,
        feature_columns=list(dataset.feature_columns),
        target_name=dataset.target_name,
        target_positive_label=1,
        threshold=0.5,
        feature_defaults=feature_defaults,
        feature_types={
            "numeric": list(dataset.numeric_columns),
            "categorical": list(dataset.categorical_columns),
        },
        model_name=winner.name,
        dataset_name=dataset.dataset_name,
        metrics={
            "selected_model": winner.name,
            "validation": winner.metrics,
            "candidate_metrics": [candidate.metrics | {"name": candidate.name} for candidate in candidate_results],
            "split": {
                "test_size": test_size,
                "random_state": random_state,
                "train_rows": int(len(X_train)),
                "validation_rows": int(len(X_valid)),
            },
            "dataset": {
                "rows": int(len(X)),
                "features": int(len(dataset.feature_columns)),
            },
        },
        feature_importance=_feature_importance(preprocessor, winner.model, list(dataset.feature_columns)),
        candidate_metrics=[candidate.metrics | {"name": candidate.name} for candidate in candidate_results],
    )

    report = {
        "bundle": bundle.to_metadata(),
        "metrics": bundle.metrics,
        "feature_count": len(bundle.feature_columns),
        "rows": int(len(X)),
    }

    if output_dir is not None:
        save_model_bundle(bundle, output_dir)

    return bundle, report


def predict_bundle(
    payload: pd.DataFrame | dict[str, Any] | list[dict[str, Any]],
    bundle: ModelBundle,
) -> list[dict[str, Any]]:
    frame = coerce_input_payload(payload, bundle.feature_columns, bundle.feature_defaults)
    encoded = bundle.preprocessor.transform(frame)
    probabilities = _safe_probability_scores(bundle.model, encoded)
    predictions = (probabilities >= bundle.threshold).astype(int)
    results: list[dict[str, Any]] = []
    for index, probability in enumerate(np.asarray(probabilities, dtype=float)):
        label = "Yes" if int(predictions[index]) == 1 else "No"
        results.append(
            {
                "probability": float(probability),
                "prediction": int(predictions[index]),
                "label": label,
                "threshold": float(bundle.threshold),
                "model_name": bundle.model_name,
                "dataset_name": bundle.dataset_name,
            }
        )
    return results
