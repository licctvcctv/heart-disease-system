from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]
if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from common.preprocessing import load_kaggle_dataframe, prepare_kaggle_frame
from common.training import train_classification_bundle


def _default_data_path() -> Path:
    return Path(__file__).resolve().parents[3] / "heart_2020_cleaned.csv"


def _default_output_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(__file__).resolve().parents[1] / "artifacts" / "kaggle_2020" / stamp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a heart disease model on heart_2020_cleaned.csv.")
    parser.add_argument("--data-path", type=Path, default=_default_data_path())
    parser.add_argument("--output-dir", type=Path, default=_default_output_dir())
    parser.add_argument("--model", default="auto", help="auto, sgd_logistic, logistic_regression, random_forest, extra_trees, xgboost, catboost")
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = load_kaggle_dataframe(args.data_path, sample_size=args.sample_size)
    dataset = prepare_kaggle_frame(frame)
    bundle, report = train_classification_bundle(
        dataset,
        output_dir=args.output_dir,
        model_name=args.model,
        test_size=args.test_size,
        random_state=args.random_state,
        sample_size=args.sample_size,
    )
    print(f"trained_model={bundle.model_name}")
    print(f"output_dir={Path(args.output_dir).resolve()}")
    print(report["metrics"]["validation"])


if __name__ == "__main__":
    main()
