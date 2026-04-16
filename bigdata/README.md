# 心脏病系统大数据层说明

本文档说明 `Hive ODS / DWD / ADS` 的导入方式与脚本使用方法。Django 分析接口默认读取 MySQL 离线 ADS 表，因此运行系统前需要先在 Hadoop/Hive 环境完成建仓，并把 ADS 同步到 MySQL。

## 目录说明

- `ddl/ods_tables.sql`：ODS 原始层建表脚本
- `dwd/dwd_clean.sql`：DWD 清洗层脚本
- `ads/ads_analysis.sql`：ADS 分析层脚本
- `scripts/load_to_hive.sh`：一键执行 ODS 建表、原始数据装载、DWD/ADS 刷新
- `scripts/sync_model_artifacts_to_hive.py`：把真实模型训练产物同步到模型 ADS 表
- `scripts/sync_hive_ads_to_mysql.py`：把 Hive ADS 离线同步到 MySQL，供 Django 快速查询
- `mysql/ads_schema.sql`：MySQL ADS 表结构
- `mapreduce/`：Java MapReduce ETL，可将原始 CSV / UCI data 清洗成 Hive 兼容 TSV

## 数据口径

统一风险字段为 `risk_label`：

- `0` = 未患病 / 非风险
- `1` = 患病 / 有风险

映射规则：

- Kaggle 2020：`HeartDisease = Yes` -> `1`，否则 `0`
- Kaggle 2022：`HadHeartAttack = Yes` 或 `HadAngina = Yes` -> `1`，否则 `0`
- UCI Cleveland：`num > 0` -> `1`，`num = 0` -> `0`

## 一键装载流程

推荐把原始文件放在项目目录：

```text
data/raw/kaggle/heart_2020_cleaned.csv
data/raw/kaggle/heart_2022_with_nans.csv
data/raw/kaggle/heart_2022_no_nans.csv
data/raw/uci/heart+disease.zip
```

然后执行：

```bash
bash bigdata/scripts/load_to_hive.sh
```

脚本会自动解压 UCI ZIP，执行 ODS/DWD/ADS SQL，并把 `ml/artifacts` 中真实训练指标写入 `ads_model_metrics` 和 `ads_model_feature_importance`。

再执行：

```bash
python3 bigdata/scripts/sync_hive_ads_to_mysql.py
```

同步完成后，Django 的分析接口读取 MySQL，不再实时查询 Hive。

## 手动导入 CSV 的标准流程

### 1. 上传文件到 HDFS

先把原始 CSV 放到 HDFS，例如：

```bash
hdfs dfs -mkdir -p /data/heart/2020
hdfs dfs -mkdir -p /data/heart/2022
hdfs dfs -put heart_2020_cleaned.csv /data/heart/2020/
hdfs dfs -put heart_2022_no_nans.csv /data/heart/2022/
hdfs dfs -put heart_2022_with_nans.csv /data/heart/2022/
```

### 2. 执行 ODS 建表脚本

先执行 `ddl/ods_tables.sql`，完成原始层建表。

### 3. 装载原始数据

Kaggle 2020 和 2022 都是带表头 CSV，通常用 `LOAD DATA` 即可：

```sql
LOAD DATA INPATH '/data/heart/2020/heart_2020_cleaned.csv'
INTO TABLE ods_heart_2020_raw;

LOAD DATA INPATH '/data/heart/2022/heart_2022_no_nans.csv'
INTO TABLE ods_heart_2022_raw;
```

如果使用 `heart_2022_with_nans.csv`，直接替换文件名即可。两份 2022 数据结构一致，清洗层会统一处理空值。
ODS 表已经配置了 `skip.header.line.count=1`，所以表头不会进入明细数据。

### 4. 执行 DWD / ADS 脚本

按顺序执行：

1. `dwd/dwd_clean.sql`
2. `ads/ads_analysis.sql`

如果后续要定期刷新分析结果，可以把 `INSERT OVERWRITE` 放进调度任务里。

## UCI zip 解压数据处理

`heart+disease.zip` 解压后，重点使用两个文件：

- `processed.cleveland.data`
- `costs/heart-disease.cost`

### 1. 解压

```bash
unzip heart+disease.zip -d heart_disease_uci
```

### 2. 上传到 HDFS

```bash
hdfs dfs -mkdir -p /data/heart/uci
hdfs dfs -mkdir -p /data/heart/uci/costs
hdfs dfs -put heart_disease_uci/processed.cleveland.data /data/heart/uci/
hdfs dfs -put heart_disease_uci/costs/heart-disease.cost /data/heart/uci/costs/
```

### 3. 导入说明

`processed.cleveland.data` 没有表头，字段之间用英文逗号分隔，缺失值用 `?` 表示，直接导入 `ods_uci_cleveland_raw` 即可。

`heart-disease.cost` 采用 `feature: cost` 的文本形式，导入 `ods_uci_cost_raw` 后，DWD 层会转成数值成本表。

## 建议执行顺序

基础 Hive SQL 路线：

1. `ddl/ods_tables.sql`
2. 导入 Kaggle 2020 / 2022 原始 CSV
3. 导入 UCI Cleveland / UCI cost 原始文本
4. `dwd/dwd_clean.sql`
5. `ads/ads_analysis.sql`

Java MapReduce ETL 路线：

1. 构建 `mapreduce/` 模块生成 jar
2. 用 `kaggle2020`、`kaggle2022`、`uci` 三种任务清洗原始数据
3. 将 MapReduce 输出 TSV 加载进 Hive 外部表或 DWD 中间表
4. 继续执行 ADS 分析 SQL

## 给 Django / Vue / Python 的对接建议

- Django REST Framework 读取 MySQL ADS 离线表，向前端返回统计 JSON
- Python 机器学习脚本优先读取 `dwd_heart_feature_sample`
- 训练后模型指标写入 `ads_model_metrics` 和 `ads_model_feature_importance`
- 前端 ECharts 直接使用 ADS 层结果绘图
