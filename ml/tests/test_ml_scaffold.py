from __future__ import annotations

import json
import zipfile
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression


KAGGLE_COLUMNS = [
    "HeartDisease",
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


def test_prepare_kaggle_frame_maps_binary_target() -> None:
    from common.preprocessing import prepare_kaggle_frame

    df = pd.DataFrame(
        [
            [
                "Yes",
                27.1,
                "Yes",
                "No",
                "No",
                2.0,
                5.0,
                "No",
                "Female",
                "55-59",
                "White",
                "No",
                "Yes",
                "Good",
                7.0,
                "No",
                "No",
                "No",
            ],
            [
                "No",
                31.4,
                "No",
                "No",
                "No",
                0.0,
                0.0,
                "No",
                "Male",
                "60-64",
                "Black",
                "Yes",
                "Yes",
                "Very good",
                8.0,
                "No",
                "No",
                "No",
            ],
        ],
        columns=KAGGLE_COLUMNS,
    )

    bundle = prepare_kaggle_frame(df)

    assert bundle.target_name == "HeartDisease"
    assert list(bundle.y.tolist()) == [1, 0]
    assert "BMI" in bundle.feature_columns
    assert bundle.X.shape == (2, 17)


def test_load_uci_cleveland_from_zip() -> None:
    from common.preprocessing import load_uci_cleveland_dataset

    root = Path(__file__).resolve().parents[3]
    zip_path = root / "heart+disease.zip"

    bundle = load_uci_cleveland_dataset(zip_path)

    assert bundle.target_name == "num"
    assert bundle.X.shape[0] == 303
    assert bundle.X.shape[1] == 13
    assert set(bundle.y.unique()).issubset({0, 1})
    assert "ca" in bundle.feature_columns


def test_predict_single_uses_saved_bundle(tmp_path: Path) -> None:
    from common.artifacts import ModelBundle, save_model_bundle
    from predict.predict import load_model_bundle, predict_single
    from common.preprocessing import build_preprocessor

    df = pd.DataFrame(
        [
            {
                "BMI": 27.1,
                "Smoking": "Yes",
                "AlcoholDrinking": "No",
                "Stroke": "No",
                "PhysicalHealth": 2.0,
                "MentalHealth": 5.0,
                "DiffWalking": "No",
                "Sex": "Female",
                "AgeCategory": "55-59",
                "Race": "White",
                "Diabetic": "No",
                "PhysicalActivity": "Yes",
                "GenHealth": "Good",
                "SleepTime": 7.0,
                "Asthma": "No",
                "KidneyDisease": "No",
                "SkinCancer": "No",
            },
            {
                "BMI": 31.4,
                "Smoking": "No",
                "AlcoholDrinking": "No",
                "Stroke": "No",
                "PhysicalHealth": 0.0,
                "MentalHealth": 0.0,
                "DiffWalking": "No",
                "Sex": "Male",
                "AgeCategory": "60-64",
                "Race": "Black",
                "Diabetic": "Yes",
                "PhysicalActivity": "Yes",
                "GenHealth": "Very good",
                "SleepTime": 8.0,
                "Asthma": "No",
                "KidneyDisease": "No",
                "SkinCancer": "No",
            },
        ]
    )
    y = pd.Series([1, 0], name="HeartDisease")

    preprocessor = build_preprocessor(df)
    model = LogisticRegression(max_iter=200)
    model.fit(preprocessor.fit_transform(df), y)

    bundle = ModelBundle(
        model=model,
        preprocessor=preprocessor,
        feature_columns=list(df.columns),
        target_name="HeartDisease",
        target_positive_label=1,
        threshold=0.5,
        feature_defaults={column: df[column].iloc[0] for column in df.columns},
        feature_types={
            "numeric": ["BMI", "PhysicalHealth", "MentalHealth", "SleepTime"],
            "categorical": [
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
            ],
        },
        model_name="logistic_regression",
        dataset_name="kaggle_2020",
    )

    output_dir = tmp_path / "bundle"
    save_model_bundle(bundle, output_dir)

    loaded = load_model_bundle(output_dir)
    result = predict_single(
        {
            "BMI": 29.0,
            "Smoking": "Yes",
            "AlcoholDrinking": "No",
            "Stroke": "No",
            "PhysicalHealth": 1.0,
            "MentalHealth": 3.0,
            "DiffWalking": "No",
            "Sex": "Female",
            "AgeCategory": "55-59",
            "Race": "White",
            "Diabetic": "No",
            "PhysicalActivity": "Yes",
            "GenHealth": "Good",
            "SleepTime": 6.0,
            "Asthma": "No",
            "KidneyDisease": "No",
            "SkinCancer": "No",
        },
        model_bundle=loaded,
    )

    assert "probability" in result
    assert "prediction" in result
    assert result["model_name"] == "logistic_regression"
    assert result["dataset_name"] == "kaggle_2020"
    assert 0.0 <= result["probability"] <= 1.0

