# 心脏病健康数据分析系统

> 面向心脏病风险分析与在线预测的毕业设计工程，采用 `Hadoop + Hive ADS + MySQL 离线指标库 + Django REST Framework + Vue3 + Python ML`。Hive 负责离线建仓，Django 默认读取 MySQL 中的离线 ADS 数据。

## 项目定位

本项目聚焦心脏病健康数据分析，覆盖数据准备、指标统计、可视化展示、模型训练、在线预测和演示答辩流程。

- 前端：Vue3 可视化页面
- 后端：Django REST Framework 提供 `/api` 接口
- 大数据层：Hadoop/Hive 完成 ODS、DWD、ADS 分层统计
- 指标源：Hive 离线生成 ADS 表后同步到 MySQL，Django 查询 MySQL 离线 ADS 表
- 模型层：Python ML 完成训练和预测，模型指标同步到 Hive ADS 表
- Java：MapReduce ETL 模块用于原始数据标准化和答辩展示

接口契约以 [docs/api_contract.md](docs/api_contract.md) 为准。

## 架构

```text
Vue3 前端
  -> Django REST Framework API
  -> MySQL 离线 ADS 指标表
  -> Python ML 在线推理

CSV / UCI ZIP
  -> HDFS / Hive ODS
  -> Hive DWD 清洗层
  -> Hive ADS 汇总层
  -> MySQL ADS 离线同步
  -> Django 查询接口
```

推荐的模块边界如下：

```text
heart-disease-system/
├─ backend/                  # Django REST Framework 后端
│  └─ django-api/
│     ├─ manage.py
│     ├─ heart_disease_api/  # settings / urls / wsgi
│     └─ apps/               # accounts / analytics / prediction
├─ frontend/                 # Vue3 前端
│  └─ vue3-app/
│     ├─ src/
│     └─ vite.config.ts
├─ data/                     # 本地数据目录（默认不提交）
│  ├─ raw/
│  ├─ processed/
│  └─ models/
├─ scripts/                  # 数据准备与辅助脚本
├─ bigdata/                  # Hive SQL 与 Java MapReduce ETL
├─ docs/
│  └─ api_contract.md
├─ docker-compose.yml
└─ .env.example
```

## 目录说明

- `backend/`：Django REST Framework 服务端，负责认证、ADS 指标查询和在线预测。
- `frontend/`：Vue3 页面，负责仪表盘、分析页、模型页和预测页展示。
- `data/raw/`：原始 CSV、UCI ZIP、临时导入文件，仅供离线建仓脚本读取。
- `data/processed/`：清洗后的训练集、特征表、导出结果。
- `data/models/`：训练产物、序列化模型、指标报告。
- `scripts/`：准备数据目录、导入辅助和本地维护脚本。

## 启动方式

### 1. 准备环境变量

```bash
cp .env.example .env
```

### 2. 准备数据目录

```bash
bash scripts/prepare_data.sh
```

### 3. Docker Compose 启动

默认启动 `mysql + backend + frontend`。分析接口读取 MySQL 中的离线 ADS 表；如果 MySQL ADS 未同步，相关接口会返回 503，不会返回静态替代数据。

```bash
docker compose up -d --build
```

### 4. 本地开发启动

后端：

```bash
cd backend/django-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

前端：

```bash
cd frontend/vue3-app
npm install
npm run dev -- --host 0.0.0.0
```

## Hive 建仓

把数据放到：

```text
data/raw/kaggle/heart_2020_cleaned.csv
data/raw/kaggle/heart_2022_with_nans.csv
data/raw/kaggle/heart_2022_no_nans.csv
data/raw/uci/heart+disease.zip
```

在 Hadoop/Hive 机器上执行：

```bash
cd heart-disease-system
bash bigdata/scripts/load_to_hive.sh
```

脚本会依次执行：

1. `bigdata/ddl/ods_tables.sql`
2. 原始数据 `LOAD DATA LOCAL INPATH` 到 ODS
3. `bigdata/dwd/dwd_clean.sql`
4. `bigdata/ads/ads_analysis.sql`
5. `bigdata/scripts/sync_model_artifacts_to_hive.py` 同步真实模型指标

然后把 Hive ADS 离线同步到 MySQL：

```bash
python bigdata/scripts/sync_hive_ads_to_mysql.py \
  --hive-host 192.168.6.129 \
  --hive-user root1 \
  --hive-database heart_disease_system \
  --mysql-host 127.0.0.1 \
  --mysql-database heart_disease \
  --mysql-user heart_user \
  --mysql-password heart_password
```

后端默认环境变量：

```bash
ANALYTICS_QUERY_ENGINE=mysql
HIVE_HOST=192.168.6.129
HIVE_PORT=10000
HIVE_USER=root1
HIVE_AUTH=NONE
HIVE_DATABASE=heart_disease_system
ADS_MYSQL_HOST=127.0.0.1
ADS_MYSQL_DATABASE=heart_disease
ADS_MYSQL_USER=heart_user
ADS_MYSQL_PASSWORD=heart_password
```

## 数据集使用

本项目支持两类常见数据源：

### 1. UCI Heart Disease

用于临床指标分析、特征解释和基础预测。建议放在：

```text
data/raw/uci/
```

使用 `heart+disease.zip`，建仓脚本会读取 `processed.cleveland.data` 和 `costs/heart-disease.cost`。

### 2. Kaggle 心脏病健康数据

用于总体分布统计、模型训练和在线预测。建议放在：

```text
data/raw/kaggle/
```

推荐保留原始文件和清洗后文件，便于复现实验和答辩展示。

### 3. 数据处理约定

- 原始数据只放在 `data/raw/`
- ODS/DWD/ADS 结果先落到 Hive，再同步到 MySQL ADS 表
- 模型文件写入 `ml/artifacts/`
- 模型评估指标同步到 Hive ADS 表
- 真实数据文件不提交到仓库

## 演示流程

1. 启动 Hadoop、Hive，执行 `bigdata/scripts/load_to_hive.sh` 生成 ODS/DWD/ADS 表。
2. 执行 `bigdata/scripts/sync_hive_ads_to_mysql.py`，把 ADS 表同步到 MySQL。
3. 启动 Django 后端和 Vue3 前端。
4. 打开前端首页，查看总览指标、年龄分析、生活方式分析和临床特征分析。
5. 进入在线预测页，填写样本特征，调用 `POST /api/predict`。
6. 展示模型指标、风险等级和特征影响因子。

## 参考接口

`docs/api_contract.md` 定义了前后端的基础数据结构和接口字段，当前 README、`.env.example` 和 `docker-compose.yml` 都按这个契约对齐。
