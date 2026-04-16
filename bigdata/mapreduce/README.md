# Java MapReduce ETL

本模块用于补齐项目中的 Java 大数据处理部分。它不替代 Hive 分层 SQL，而是在 Hive 之前提供一个可选 ETL 步骤：把不同来源的原始 CSV / data 文件清洗成统一 TSV，方便后续加载到 Hive。

## 作用定位

```text
原始 CSV / UCI data
  -> Java MapReduce 清洗
  -> HDFS TSV 输出
  -> Hive DWD / dwd_heart_feature_sample
  -> ADS 分析 / Python ML
```

输出字段统一为：

```text
source_dataset
risk_label
age_band
sex_code
bmi
physical_health_days
mental_health_days
smoking_flag
alcohol_flag
activity_flag
sleep_metric
stroke_flag
diabetes_flag
kidney_flag
asthma_flag
skin_cancer_flag
chest_pain_type
resting_bp
cholesterol
max_heart_rate
exercise_angina_flag
st_depression
slope
vessel_count
thal
```

其中 `risk_label` 统一为：

- `0`：未患病 / 非风险
- `1`：患病 / 有风险

## 构建

```bash
cd heart-disease-system/bigdata/mapreduce
mvn -q -DskipTests package
```

构建产物：

```text
target/heart-disease-mapreduce-etl-0.1.0.jar
```

## 运行

命令格式：

```bash
hadoop jar target/heart-disease-mapreduce-etl-0.1.0.jar <dataset> <input> <output>
```

支持的数据集参数：

- `kaggle2020`：处理 `heart_2020_cleaned.csv`
- `kaggle2022`：处理 `heart_2022_no_nans.csv` 或 `heart_2022_with_nans.csv`
- `uci`：处理 `processed.cleveland.data`

示例：

```bash
hdfs dfs -mkdir -p /data/heart/raw /data/heart/mr
hdfs dfs -put heart_2020_cleaned.csv /data/heart/raw/

hadoop jar target/heart-disease-mapreduce-etl-0.1.0.jar \
  kaggle2020 \
  /data/heart/raw/heart_2020_cleaned.csv \
  /data/heart/mr/kaggle2020_feature_sample
```

输出可以用 Hive 外部表读取：

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS dwd_heart_feature_sample_mr (
  source_dataset string,
  risk_label int,
  age_band string,
  sex_code int,
  bmi decimal(6,2),
  physical_health_days int,
  mental_health_days int,
  smoking_flag int,
  alcohol_flag int,
  activity_flag int,
  sleep_metric decimal(6,2),
  stroke_flag int,
  diabetes_flag int,
  kidney_flag int,
  asthma_flag int,
  skin_cancer_flag int,
  chest_pain_type int,
  resting_bp decimal(6,1),
  cholesterol decimal(6,1),
  max_heart_rate decimal(6,1),
  exercise_angina_flag int,
  st_depression decimal(6,2),
  slope int,
  vessel_count int,
  thal int
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/data/heart/mr/kaggle2020_feature_sample';
```

## 说明

- MapReduce 输出中的空值使用 Hive 兼容的 `\N`。
- 2022 数据中包含带逗号的文本字段，因此代码使用 `commons-csv` 解析，而不是简单 `split(",")`。
- 该模块是 Hive 建仓前的 Java ETL 增强路径，论文和答辩中可用它体现 MapReduce 处理流程。
