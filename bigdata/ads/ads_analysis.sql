-- =========================================================
-- 心脏病健康数据分析系统
-- ADS 应用分析层 SQL
-- 说明：
-- 1. 本层面向前端 ECharts 展示和 Django REST API 查询。
-- 2. 结果表以分析场景划分，便于论文答辩演示和接口对接。
-- 3. 如需定时刷新，可用外部调度任务执行 INSERT OVERWRITE。
-- =========================================================

CREATE DATABASE IF NOT EXISTS heart_disease_system;
USE heart_disease_system;

-- ---------------------------------------------------------
-- 1) 数据集总览
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_heart_overview;
CREATE TABLE ads_heart_overview (
    dataset_name        STRING COMMENT '数据集名称',
    sample_count        BIGINT COMMENT '样本数',
    positive_count      BIGINT COMMENT '患病/有风险样本数',
    negative_count      BIGINT COMMENT '未患病/非风险样本数',
    prevalence_rate     DECIMAL(8,4) COMMENT '患病率',
    source_file         STRING COMMENT '来源文件',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE ads_heart_overview
SELECT
    dataset_name,
    sample_count,
    positive_count,
    negative_count,
    CAST(
        CASE
            WHEN sample_count = 0 THEN 0
            ELSE CAST(positive_count AS DECIMAL(18,6)) / CAST(sample_count AS DECIMAL(18,6))
        END
    AS DECIMAL(8,4)) AS prevalence_rate,
    source_file,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM (
    SELECT
        source_dataset AS dataset_name,
        COUNT(1) AS sample_count,
        SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS positive_count,
        SUM(CASE WHEN risk_label = 0 THEN 1 ELSE 0 END) AS negative_count,
        max(source_file) AS source_file
    FROM dwd_heart_feature_sample
    GROUP BY source_dataset
) t;

-- ---------------------------------------------------------
-- 2) 年龄段分析
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_heart_by_age;
CREATE TABLE ads_heart_by_age (
    dataset_name        STRING COMMENT '数据集名称',
    age_band            STRING COMMENT '年龄段',
    sample_count        BIGINT COMMENT '样本数',
    positive_count      BIGINT COMMENT '患病数',
    prevalence_rate     DECIMAL(8,4) COMMENT '患病率',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE ads_heart_by_age
SELECT
    source_dataset AS dataset_name,
    age_band,
    COUNT(1) AS sample_count,
    SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS positive_count,
    CAST(
        CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
        / CAST(COUNT(1) AS DECIMAL(18,6))
    AS DECIMAL(8,4)) AS prevalence_rate,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM dwd_heart_feature_sample
GROUP BY source_dataset, age_band;

-- ---------------------------------------------------------
-- 3) 性别分析
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_heart_by_sex;
CREATE TABLE ads_heart_by_sex (
    dataset_name        STRING COMMENT '数据集名称',
    sex_code            INT COMMENT '性别编码',
    sex_label           STRING COMMENT '性别标签',
    sample_count        BIGINT COMMENT '样本数',
    positive_count      BIGINT COMMENT '患病数',
    prevalence_rate     DECIMAL(8,4) COMMENT '患病率',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE ads_heart_by_sex
SELECT
    source_dataset AS dataset_name,
    sex_code,
    CASE WHEN sex_code = 1 THEN 'Male' ELSE 'Female' END AS sex_label,
    COUNT(1) AS sample_count,
    SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS positive_count,
    CAST(
        CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
        / CAST(COUNT(1) AS DECIMAL(18,6))
    AS DECIMAL(8,4)) AS prevalence_rate,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM dwd_heart_feature_sample
WHERE sex_code IS NOT NULL
GROUP BY source_dataset, sex_code;

-- ---------------------------------------------------------
-- 4) BMI 分组分析
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_heart_by_bmi;
CREATE TABLE ads_heart_by_bmi (
    dataset_name        STRING COMMENT '数据集名称',
    bmi_group           STRING COMMENT 'BMI 分组',
    sample_count        BIGINT COMMENT '样本数',
    positive_count      BIGINT COMMENT '患病数',
    prevalence_rate     DECIMAL(8,4) COMMENT '患病率',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE ads_heart_by_bmi
SELECT
    source_dataset AS dataset_name,
    CASE
        WHEN bmi IS NULL THEN 'Unknown'
        WHEN bmi < 18.5 THEN 'Underweight'
        WHEN bmi < 24 THEN 'Normal'
        WHEN bmi < 28 THEN 'Overweight'
        ELSE 'Obese'
    END AS bmi_group,
    COUNT(1) AS sample_count,
    SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS positive_count,
    CAST(
        CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
        / CAST(COUNT(1) AS DECIMAL(18,6))
    AS DECIMAL(8,4)) AS prevalence_rate,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM dwd_heart_feature_sample
WHERE source_dataset IN ('kaggle_2020', 'kaggle_2022')
GROUP BY source_dataset,
    CASE
        WHEN bmi IS NULL THEN 'Unknown'
        WHEN bmi < 18.5 THEN 'Underweight'
        WHEN bmi < 24 THEN 'Normal'
        WHEN bmi < 28 THEN 'Overweight'
        ELSE 'Obese'
    END;

-- ---------------------------------------------------------
-- 5) 生活方式分析
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_heart_lifestyle;
CREATE TABLE ads_heart_lifestyle (
    dataset_name        STRING COMMENT '数据集名称',
    factor_name         STRING COMMENT '分析因子',
    factor_value        STRING COMMENT '因子取值',
    sample_count        BIGINT COMMENT '样本数',
    positive_count      BIGINT COMMENT '患病数',
    prevalence_rate     DECIMAL(8,4) COMMENT '患病率',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE ads_heart_lifestyle
SELECT * FROM (
    SELECT source_dataset, 'smoking_flag' AS factor_name, CAST(smoking_flag AS STRING) AS factor_value,
           COUNT(1) AS sample_count, SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS positive_count,
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)) AS prevalence_rate,
           date_format(current_date(), 'yyyy-MM-dd') AS load_dt
    FROM dwd_heart_feature_sample
    WHERE smoking_flag IS NOT NULL
    GROUP BY source_dataset, smoking_flag
    UNION ALL
    SELECT source_dataset, 'alcohol_flag', CAST(alcohol_flag AS STRING),
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE alcohol_flag IS NOT NULL
    GROUP BY source_dataset, alcohol_flag
    UNION ALL
    SELECT source_dataset, 'activity_flag', CAST(activity_flag AS STRING),
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE activity_flag IS NOT NULL
    GROUP BY source_dataset, activity_flag
    UNION ALL
    SELECT source_dataset, 'sleep_metric',
           CASE
               WHEN sleep_metric < 6 THEN 'Short(<6)'
               WHEN sleep_metric <= 8 THEN 'Normal(6-8)'
               ELSE 'Long(>8)'
           END,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE sleep_metric IS NOT NULL
    GROUP BY source_dataset,
             CASE
                 WHEN sleep_metric < 6 THEN 'Short(<6)'
                 WHEN sleep_metric <= 8 THEN 'Normal(6-8)'
                 ELSE 'Long(>8)'
             END
) t;

-- ---------------------------------------------------------
-- 6) 共病分析
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_heart_comorbidity;
CREATE TABLE ads_heart_comorbidity (
    dataset_name        STRING COMMENT '数据集名称',
    disease_name        STRING COMMENT '共病名称',
    disease_flag        INT COMMENT '是否存在(1/0)',
    sample_count        BIGINT COMMENT '样本数',
    positive_count      BIGINT COMMENT '患病数',
    prevalence_rate     DECIMAL(8,4) COMMENT '患病率',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE ads_heart_comorbidity
SELECT * FROM (
    SELECT source_dataset, 'stroke' AS disease_name, stroke_flag AS disease_flag,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE stroke_flag IS NOT NULL
    GROUP BY source_dataset, stroke_flag
    UNION ALL
    SELECT source_dataset, 'diabetes', diabetes_flag,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE diabetes_flag IS NOT NULL
    GROUP BY source_dataset, diabetes_flag
    UNION ALL
    SELECT source_dataset, 'kidney_disease', kidney_flag,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE kidney_flag IS NOT NULL
    GROUP BY source_dataset, kidney_flag
    UNION ALL
    SELECT source_dataset, 'asthma', asthma_flag,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE asthma_flag IS NOT NULL
    GROUP BY source_dataset, asthma_flag
    UNION ALL
    SELECT source_dataset, 'skin_cancer', skin_cancer_flag,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE skin_cancer_flag IS NOT NULL
    GROUP BY source_dataset, skin_cancer_flag
) t;

-- ---------------------------------------------------------
-- 7) UCI 临床指标分析
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_uci_clinical_risk;
CREATE TABLE ads_uci_clinical_risk (
    feature_name        STRING COMMENT '字段名',
    feature_label       STRING COMMENT '字段中文名',
    feature_value       STRING COMMENT '取值',
    sample_count        BIGINT COMMENT '样本数',
    positive_count      BIGINT COMMENT '患病数',
    prevalence_rate     DECIMAL(8,4) COMMENT '患病率',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE ads_uci_clinical_risk
SELECT * FROM (
    SELECT 'cp' AS feature_name, '胸痛类型' AS feature_label, CAST(chest_pain_type AS STRING) AS feature_value,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND chest_pain_type IS NOT NULL
    GROUP BY chest_pain_type
    UNION ALL
    SELECT 'sex_code', '性别', CAST(sex_code AS STRING),
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND sex_code IS NOT NULL
    GROUP BY sex_code
    UNION ALL
    SELECT 'thal', '铊扫描结果', CAST(thal AS STRING),
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND thal IS NOT NULL
    GROUP BY thal
    UNION ALL
    SELECT 'trestbps', '静息血压',
           CASE
               WHEN resting_bp < 120 THEN 'normal'
               WHEN resting_bp < 140 THEN 'elevated'
               ELSE 'high'
           END,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND resting_bp IS NOT NULL
    GROUP BY
           CASE
               WHEN resting_bp < 120 THEN 'normal'
               WHEN resting_bp < 140 THEN 'elevated'
               ELSE 'high'
           END
    UNION ALL
    SELECT 'chol', '血清胆固醇',
           CASE
               WHEN cholesterol < 200 THEN 'desirable'
               WHEN cholesterol < 240 THEN 'borderline'
               ELSE 'high'
           END,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND cholesterol IS NOT NULL
    GROUP BY
           CASE
               WHEN cholesterol < 200 THEN 'desirable'
               WHEN cholesterol < 240 THEN 'borderline'
               ELSE 'high'
           END
    UNION ALL
    SELECT 'thalach', '最大心率',
           CASE
               WHEN max_heart_rate < 120 THEN 'low'
               WHEN max_heart_rate < 160 THEN 'medium'
               ELSE 'high'
           END,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND max_heart_rate IS NOT NULL
    GROUP BY
           CASE
               WHEN max_heart_rate < 120 THEN 'low'
               WHEN max_heart_rate < 160 THEN 'medium'
               ELSE 'high'
           END
    UNION ALL
    SELECT 'exang', '运动诱发心绞痛', CAST(exercise_angina_flag AS STRING),
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND exercise_angina_flag IS NOT NULL
    GROUP BY exercise_angina_flag
    UNION ALL
    SELECT 'oldpeak', 'ST 段压低',
           CASE
               WHEN st_depression < 1 THEN 'low'
               WHEN st_depression < 2 THEN 'medium'
               ELSE 'high'
           END,
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND st_depression IS NOT NULL
    GROUP BY
           CASE
               WHEN st_depression < 1 THEN 'low'
               WHEN st_depression < 2 THEN 'medium'
               ELSE 'high'
           END
    UNION ALL
    SELECT 'slope', 'ST 段斜率', CAST(slope AS STRING),
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND slope IS NOT NULL
    GROUP BY slope
    UNION ALL
    SELECT 'ca', '主要血管数', CAST(vessel_count AS STRING),
           COUNT(1), SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END),
           CAST(
               CAST(SUM(CASE WHEN risk_label = 1 THEN 1 ELSE 0 END) AS DECIMAL(18,6))
               / CAST(COUNT(1) AS DECIMAL(18,6))
           AS DECIMAL(8,4)),
           date_format(current_date(), 'yyyy-MM-dd')
    FROM dwd_heart_feature_sample
    WHERE source_dataset = 'uci_cleveland' AND vessel_count IS NOT NULL
    GROUP BY vessel_count
) t;

-- ---------------------------------------------------------
-- 8) UCI 成本分析
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_uci_cost_analysis;
CREATE TABLE ads_uci_cost_analysis (
    feature             STRING COMMENT '检查项目名称',
    cost                DECIMAL(10,2) COMMENT '独立检查成本',
    cost_rank           INT COMMENT '成本排名',
    cost_level          STRING COMMENT '成本层级',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE ads_uci_cost_analysis
SELECT
    feature,
    cost,
    cost_rank,
    CASE
        WHEN cost <= 5 THEN 'low'
        WHEN cost <= 50 THEN 'medium'
        ELSE 'high'
    END AS cost_level,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM dwd_uci_cost_clean;

-- ---------------------------------------------------------
-- 9) 模型指标表
-- 说明：
-- - 该表由 Python 训练脚本或 bigdata/scripts/sync_model_artifacts_to_hive.py 写入
-- - Django 接口只查询 ADS 表，不再从本地文件拼接分析指标
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ads_model_metrics;
CREATE TABLE ads_model_metrics (
    model_name          STRING COMMENT '模型名称',
    accuracy            DECIMAL(8,4) COMMENT '准确率',
    precision_score     DECIMAL(8,4) COMMENT '精确率',
    recall_score        DECIMAL(8,4) COMMENT '召回率',
    f1_score            DECIMAL(8,4) COMMENT 'F1 值',
    auc                 DECIMAL(8,4) COMMENT 'AUC',
    train_dataset       STRING COMMENT '训练数据集',
    note                STRING COMMENT '备注',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;

DROP TABLE IF EXISTS ads_model_feature_importance;
CREATE TABLE ads_model_feature_importance (
    model_name          STRING COMMENT '模型名称',
    feature_name        STRING COMMENT '特征名',
    feature_label       STRING COMMENT '特征中文名',
    importance          DECIMAL(12,6) COMMENT '重要性',
    train_dataset       STRING COMMENT '训练数据集',
    load_dt             STRING COMMENT '统计日期'
)
STORED AS ORC;
