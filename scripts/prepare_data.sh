#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="$ROOT_DIR/data/raw"
UCI_DIR="$RAW_DIR/uci"
KAGGLE_DIR="$RAW_DIR/kaggle"
PROCESSED_DIR="$ROOT_DIR/data/processed"
MODEL_DIR="$ROOT_DIR/data/models"

mkdir -p "$UCI_DIR" "$KAGGLE_DIR" "$PROCESSED_DIR" "$MODEL_DIR"

cat <<EOF
Data directories are ready:
  - $RAW_DIR
  - $UCI_DIR
  - $KAGGLE_DIR
  - $PROCESSED_DIR
  - $MODEL_DIR

Next steps:
  1. Copy CSV files into:
     - $KAGGLE_DIR
     - $UCI_DIR
  2. Or unzip the UCI dataset into:
     - $UCI_DIR
  3. Keep raw source files out of git. They are ignored by .gitignore.

Example commands:
  cp /path/to/heart.csv "$KAGGLE_DIR"/
  unzip /path/to/uci_heart_disease.zip -d "$UCI_DIR"
EOF
