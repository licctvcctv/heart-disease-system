from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

KAGGLE_TARGET_COL = "HeartDisease"
KAGGLE_FEATURE_COLUMNS = [
    "BMI",
    "Smoking",
    "AlcoholDrinking",
    "Stroke",
    "PhysicalHealth",
    "MentalHealth",
    "DiffWalking",
    "Sex",
    "AgeCategory",
    "Race",
    "Diabetic",
    "PhysicalActivity",
    "GenHealth",
    "SleepTime",
    "Asthma",
    "KidneyDisease",
    "SkinCancer",
]
KAGGLE_NUMERIC_COLUMNS = [
    "BMI",
    "PhysicalHealth",
    "MentalHealth",
    "SleepTime",
]
KAGGLE_CATEGORICAL_COLUMNS = [
    "Smoking",
    "AlcoholDrinking",
    "Stroke",
    "DiffWalking",
    "Sex",
    "AgeCategory",
    "Race",
    "Diabetic",
    "PhysicalActivity",
    "GenHealth",
    "Asthma",
    "KidneyDisease",
    "SkinCancer",
]

UCI_TARGET_COL = "num"
UCI_FEATURE_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]
UCI_NUMERIC_COLUMNS = [
    "age",
    "trestbps",
    "chol",
    "thalach",
    "oldpeak",
]
UCI_CATEGORICAL_COLUMNS = [
    "sex",
    "cp",
    "fbs",
    "restecg",
    "exang",
    "slope",
    "ca",
    "thal",
]


@dataclass(slots=True)
class DatasetBundle:
    X: pd.DataFrame
    y: pd.Series
    feature_columns: list[str]
    target_name: str
    dataset_name: str
    numeric_columns: list[str]
    categorical_columns: list[str]
    source_path: str | None = None


def _ensure_path(path: str | Path) -> Path:
    return path if isinstance(path, Path) else Path(path)


def _normalize_text_value(value: Any) -> Any:
    if pd.isna(value):
        return np.nan
    if isinstance(value, str):
        text = value.strip()
        if text in {"", "nan", "None", "null"}:
            return np.nan
        return text
    return value


def _one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def load_kaggle_dataframe(path: str | Path, sample_size: int | None = None) -> pd.DataFrame:
    csv_path = _ensure_path(path)
    read_kwargs: dict[str, Any] = {}
    if sample_size is not None:
        read_kwargs["nrows"] = int(sample_size)
    return pd.read_csv(csv_path, **read_kwargs)


def prepare_kaggle_frame(df: pd.DataFrame) -> DatasetBundle:
    missing = [column for column in [KAGGLE_TARGET_COL, *KAGGLE_FEATURE_COLUMNS] if column not in df.columns]
    if missing:
        raise ValueError(f"Missing Kaggle columns: {missing}")

    prepared = df[[KAGGLE_TARGET_COL, *KAGGLE_FEATURE_COLUMNS]].copy()
    for column in prepared.columns:
        prepared[column] = prepared[column].map(_normalize_text_value)

    y = prepared[KAGGLE_TARGET_COL].map({"Yes": 1, "No": 0, 1: 1, 0: 0}).astype("Int64")
    if y.isna().any():
        raise ValueError("Kaggle target column contains values that cannot be mapped to binary labels.")

    X = prepared[KAGGLE_FEATURE_COLUMNS].copy()
    for column in KAGGLE_NUMERIC_COLUMNS:
        X[column] = pd.to_numeric(X[column], errors="coerce")
    for column in KAGGLE_CATEGORICAL_COLUMNS:
        X[column] = X[column].map(_normalize_text_value).astype(object)

    return DatasetBundle(
        X=X,
        y=y.astype(int),
        feature_columns=list(KAGGLE_FEATURE_COLUMNS),
        target_name=KAGGLE_TARGET_COL,
        dataset_name="kaggle_2020",
        numeric_columns=list(KAGGLE_NUMERIC_COLUMNS),
        categorical_columns=list(KAGGLE_CATEGORICAL_COLUMNS),
    )


def _load_uci_raw_frame(path: str | Path) -> pd.DataFrame:
    raw_path = _ensure_path(path)
    columns = [*UCI_FEATURE_COLUMNS, UCI_TARGET_COL]
    if raw_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(raw_path) as archive:
            candidate_names = [
                "processed.cleveland.data",
                "cleveland.data",
            ]
            for candidate in candidate_names:
                try:
                    with archive.open(candidate) as handle:
                        text_handle = io.TextIOWrapper(handle, encoding="utf-8")
                        return pd.read_csv(
                            text_handle,
                            header=None,
                            names=columns,
                            na_values=["?"],
                            skipinitialspace=True,
                        )
                except KeyError:
                    continue
            raise FileNotFoundError("processed.cleveland.data not found inside zip archive.")
    return pd.read_csv(
        raw_path,
        header=None,
        names=columns,
        na_values=["?"],
        skipinitialspace=True,
    )


def prepare_uci_frame(df: pd.DataFrame) -> DatasetBundle:
    missing = [column for column in [*UCI_FEATURE_COLUMNS, UCI_TARGET_COL] if column not in df.columns]
    if missing:
        raise ValueError(f"Missing UCI columns: {missing}")

    prepared = df[[*UCI_FEATURE_COLUMNS, UCI_TARGET_COL]].copy()
    prepared = prepared.replace({"?": np.nan})

    for column in UCI_NUMERIC_COLUMNS:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce")
    for column in UCI_CATEGORICAL_COLUMNS:
        prepared[column] = prepared[column].map(_normalize_text_value).astype(object)

    y = pd.to_numeric(prepared[UCI_TARGET_COL], errors="coerce")
    if y.isna().any():
        raise ValueError("UCI target column contains values that cannot be mapped to binary labels.")
    y = (y > 0).astype(int)

    X = prepared[UCI_FEATURE_COLUMNS].copy()
    return DatasetBundle(
        X=X,
        y=y,
        feature_columns=list(UCI_FEATURE_COLUMNS),
        target_name=UCI_TARGET_COL,
        dataset_name="uci_cleveland",
        numeric_columns=list(UCI_NUMERIC_COLUMNS),
        categorical_columns=list(UCI_CATEGORICAL_COLUMNS),
    )


def load_uci_cleveland_dataset(path: str | Path) -> DatasetBundle:
    return prepare_uci_frame(_load_uci_raw_frame(path))


def build_feature_defaults(
    df: pd.DataFrame,
    numeric_columns: Sequence[str],
    categorical_columns: Sequence[str],
) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for column in numeric_columns:
        series = pd.to_numeric(df[column], errors="coerce")
        value = series.median()
        defaults[column] = None if pd.isna(value) else float(value)
    for column in categorical_columns:
        series = df[column].astype(object)
        mode = series.mode(dropna=True)
        defaults[column] = mode.iloc[0] if not mode.empty else None
    return defaults


def build_preprocessor(
    df: pd.DataFrame,
    numeric_columns: Sequence[str] | None = None,
    categorical_columns: Sequence[str] | None = None,
) -> ColumnTransformer:
    if numeric_columns is None or categorical_columns is None:
        numeric_columns = list(df.select_dtypes(include=["number", "bool"]).columns)
        categorical_columns = [column for column in df.columns if column not in set(numeric_columns)]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", _one_hot_encoder()),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, list(numeric_columns)),
            ("categorical", categorical_pipeline, list(categorical_columns)),
        ],
        remainder="drop",
    )


def coerce_input_payload(
    payload: pd.DataFrame | dict[str, Any] | Sequence[dict[str, Any]],
    feature_columns: Sequence[str],
    feature_defaults: dict[str, Any] | None = None,
) -> pd.DataFrame:
    if isinstance(payload, pd.DataFrame):
        frame = payload.copy()
    elif isinstance(payload, dict):
        frame = pd.DataFrame([payload])
    elif isinstance(payload, Sequence):
        frame = pd.DataFrame(list(payload))
    else:
        raise TypeError("payload must be a pandas DataFrame, a mapping, or a sequence of mappings.")

    frame = frame.reindex(columns=list(feature_columns))
    defaults = feature_defaults or {}
    for column in feature_columns:
        default_value = defaults.get(column, np.nan)
        if column not in frame.columns:
            frame[column] = default_value
        else:
            frame[column] = frame[column].where(frame[column].notna(), default_value)
    return frame[list(feature_columns)]
