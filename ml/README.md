# Heart Disease ML Module

This directory contains the standalone Python ML scaffold for the heart disease system.

## Layout

- `common/`: shared preprocessing, artifact management, and training helpers
- `train/`: dataset-specific training entrypoints
- `predict/`: stable inference API for Django

## Dependencies

Install the minimal stack:

```bash
pip install -r requirements.txt
```

Optional models:

- `xgboost`
- `catboost`

They are detected dynamically. Basic training still works without them.

## Training

Run from the `heart-disease-system/ml` directory or any environment where this directory is on `PYTHONPATH`.

```bash
python train/train_kaggle.py
python train/train_uci.py
```

Useful flags:

- `--data-path`: override the dataset path
- `--output-dir`: choose where artifacts are written
- `--model`: pick `auto`, `sgd_logistic`, `logistic_regression`, `random_forest`, `extra_trees`
- `--sample-size`: downsample large Kaggle runs for quicker iteration

Artifacts written to the output directory:

- `model.joblib`
- `metrics.json`
- `feature_importance.json`
- `fields.json`
- `metadata.json`

## Django Usage

Add `heart-disease-system/ml` to `PYTHONPATH`, then import:

```python
from predict.predict import load_model_bundle, predict_single

bundle = load_model_bundle("/path/to/artifacts/run_dir")
result = predict_single(payload_dict, model_bundle=bundle)
```

The returned object contains:

- `prediction`
- `probability`
- `label`
- `threshold`
- `model_name`
- `dataset_name`

## Notes

- Kaggle 2020 uses `HeartDisease` as the binary target.
- UCI Cleveland uses `num > 0` as the positive class.
- Missing values in `processed.cleveland.data` are parsed from `?`.

