#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIGDATA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$(cd "$BIGDATA_DIR/.." && pwd)"

export HADOOP_HOME="${HADOOP_HOME:-/opt/hadoop-3.3.6}"
export HIVE_HOME="${HIVE_HOME:-/opt/apache-hive-3.1.3-bin}"
export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin:$PATH"

RAW_DATA_DIR="${RAW_DATA_DIR:-$PROJECT_DIR/data/raw}"
KAGGLE_DATASET_DIR="${KAGGLE_DATASET_DIR:-$RAW_DATA_DIR/kaggle}"
UCI_DATASET_DIR="${UCI_DATASET_DIR:-$RAW_DATA_DIR/uci}"
MODEL_DIR="${ML_MODEL_DIR:-$PROJECT_DIR/ml/artifacts/smoke/kaggle_2020}"
HIVE_DATABASE="${HIVE_DATABASE:-heart_disease_system}"
HIVE_REPLICATION="${HIVE_REPLICATION:-1}"
HIVE_CMD=(hive --hiveconf "dfs.replication=$HIVE_REPLICATION")

KAGGLE_2020_FILE="${KAGGLE_2020_FILE:-$KAGGLE_DATASET_DIR/heart_2020_cleaned.csv}"
KAGGLE_2022_FILE="${KAGGLE_2022_FILE:-$KAGGLE_DATASET_DIR/heart_2022_with_nans.csv}"
if [[ ! -f "$KAGGLE_2022_FILE" ]]; then
  KAGGLE_2022_FILE="$KAGGLE_DATASET_DIR/heart_2022_no_nans.csv"
fi
UCI_ZIP_FILE="${UCI_ZIP_FILE:-$UCI_DATASET_DIR/heart+disease.zip}"

for file in "$KAGGLE_2020_FILE" "$KAGGLE_2022_FILE" "$UCI_ZIP_FILE"; do
  if [[ ! -f "$file" ]]; then
    echo "Missing required source file: $file" >&2
    exit 1
  fi
done

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
unzip -p "$UCI_ZIP_FILE" processed.cleveland.data > "$TMP_DIR/processed.cleveland.data"
unzip -p "$UCI_ZIP_FILE" costs/heart-disease.cost > "$TMP_DIR/heart-disease.cost"

"${HIVE_CMD[@]}" -f "$BIGDATA_DIR/ddl/ods_tables.sql"

"${HIVE_CMD[@]}" -e "
USE $HIVE_DATABASE;
LOAD DATA LOCAL INPATH '$KAGGLE_2020_FILE' OVERWRITE INTO TABLE ods_heart_2020_raw;
LOAD DATA LOCAL INPATH '$KAGGLE_2022_FILE' OVERWRITE INTO TABLE ods_heart_2022_raw;
LOAD DATA LOCAL INPATH '$TMP_DIR/processed.cleveland.data' OVERWRITE INTO TABLE ods_uci_cleveland_raw;
LOAD DATA LOCAL INPATH '$TMP_DIR/heart-disease.cost' OVERWRITE INTO TABLE ods_uci_cost_raw;
"

"${HIVE_CMD[@]}" -f "$BIGDATA_DIR/dwd/dwd_clean.sql"
"${HIVE_CMD[@]}" -f "$BIGDATA_DIR/ads/ads_analysis.sql"

if [[ -d "$MODEL_DIR" ]]; then
  python3 "$SCRIPT_DIR/sync_model_artifacts_to_hive.py" \
    --model-dir "$MODEL_DIR" \
    --dataset kaggle_2020 \
    --hive-database "$HIVE_DATABASE" \
    --hive-replication "$HIVE_REPLICATION" \
    --execute
else
  echo "Model artifact directory not found, skipped model ADS sync: $MODEL_DIR" >&2
fi

if [[ "${SYNC_ADS_TO_MYSQL:-0}" == "1" ]]; then
  python3 "$SCRIPT_DIR/sync_hive_ads_to_mysql.py"
fi

echo "Hive warehouse load finished: $HIVE_DATABASE"
