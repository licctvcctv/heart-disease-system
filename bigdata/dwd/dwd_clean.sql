-- =========================================================
-- 心脏病健康数据分析系统
-- DWD 明细清洗层 SQL
-- 说明：
-- 1. 统一 risk_label：0=未患病/非风险，1=患病/有风险。
-- 2. Kaggle 2020 / 2022、UCI Cleveland、UCI cost 均转换到标准明细结构。
-- 3. SQL 以可读性为主，便于毕业设计答辩展示。
-- =========================================================

CREATE DATABASE IF NOT EXISTS heart_disease_system;
USE heart_disease_system;

-- ---------------------------------------------------------
-- 1) Kaggle 2020 清洗表
-- ---------------------------------------------------------
DROP TABLE IF EXISTS dwd_heart_2020_clean;
CREATE TABLE dwd_heart_2020_clean (
    source_dataset      STRING COMMENT '数据来源名称',
    source_file         STRING COMMENT '原始文件名',
    risk_label          INT COMMENT '0=未患病/非风险,1=患病/有风险',
    bmi                 DECIMAL(6,2) COMMENT 'BMI',
    smoking_flag        INT COMMENT '是否吸烟(1=是,0=否)',
    alcohol_flag        INT COMMENT '是否饮酒过量(1=是,0=否)',
    stroke_flag         INT COMMENT '是否中风史(1=是,0=否)',
    physical_health_days INT COMMENT '过去30天身体不适天数',
    mental_health_days  INT COMMENT '过去30天心理不适天数',
    diff_walking_flag   INT COMMENT '行走是否困难(1=是,0=否)',
    sex_code            INT COMMENT '性别(1=男,0=女)',
    age_category        STRING COMMENT '年龄段',
    race                STRING COMMENT '种族',
    diabetic_text       STRING COMMENT '糖尿病原始值',
    diabetic_flag       INT COMMENT '糖尿病是否存在(1=是,0=否/未知)',
    physical_activity_flag INT COMMENT '是否有身体活动(1=是,0=否)',
    gen_health          STRING COMMENT '总体健康状况',
    sleep_time          INT COMMENT '睡眠时长(小时)',
    asthma_flag         INT COMMENT '哮喘(1=是,0=否)',
    kidney_disease_flag INT COMMENT '肾病(1=是,0=否)',
    skin_cancer_flag    INT COMMENT '皮肤癌(1=是,0=否)',
    load_dt             STRING COMMENT '装载日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE dwd_heart_2020_clean
SELECT
    'kaggle_2020' AS source_dataset,
    'heart_2020_cleaned.csv' AS source_file,
    CASE WHEN lower(trim(heart_disease)) = 'yes' THEN 1 ELSE 0 END AS risk_label,
    CAST(NULLIF(trim(bmi), '') AS DECIMAL(6,2)) AS bmi,
    CASE WHEN lower(trim(smoking)) = 'yes' THEN 1 ELSE 0 END AS smoking_flag,
    CASE WHEN lower(trim(alcohol_drinking)) = 'yes' THEN 1 ELSE 0 END AS alcohol_flag,
    CASE WHEN lower(trim(stroke)) = 'yes' THEN 1 ELSE 0 END AS stroke_flag,
    CAST(NULLIF(trim(physical_health), '') AS INT) AS physical_health_days,
    CAST(NULLIF(trim(mental_health), '') AS INT) AS mental_health_days,
    CASE WHEN lower(trim(diff_walking)) = 'yes' THEN 1 ELSE 0 END AS diff_walking_flag,
    CASE WHEN lower(trim(sex)) = 'male' THEN 1 ELSE 0 END AS sex_code,
    trim(age_category) AS age_category,
    trim(race) AS race,
    trim(diabetic) AS diabetic_text,
    CASE
        WHEN lower(trim(diabetic)) IN ('yes', 'yes (during pregnancy)', 'yes, but female') THEN 1
        ELSE 0
    END AS diabetic_flag,
    CASE WHEN lower(trim(physical_activity)) = 'yes' THEN 1 ELSE 0 END AS physical_activity_flag,
    trim(gen_health) AS gen_health,
    CAST(NULLIF(trim(sleep_time), '') AS INT) AS sleep_time,
    CASE WHEN lower(trim(asthma)) = 'yes' THEN 1 ELSE 0 END AS asthma_flag,
    CASE WHEN lower(trim(kidney_disease)) = 'yes' THEN 1 ELSE 0 END AS kidney_disease_flag,
    CASE WHEN lower(trim(skin_cancer)) = 'yes' THEN 1 ELSE 0 END AS skin_cancer_flag,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM ods_heart_2020_raw;

-- ---------------------------------------------------------
-- 2) Kaggle 2022 清洗表
-- 说明：
-- - 可加载 heart_2022_no_nans.csv，也可加载 heart_2022_with_nans.csv
-- - 缺失值统一转换为 NULL 或默认值
-- - HeartAttack / Angina 统一映射到 risk_label
-- ---------------------------------------------------------
DROP TABLE IF EXISTS dwd_heart_2022_clean;
CREATE TABLE dwd_heart_2022_clean (
    source_dataset      STRING COMMENT '数据来源名称',
    source_file         STRING COMMENT '原始文件名',
    risk_label          INT COMMENT '0=未患病/非风险,1=患病/有风险',
    state               STRING COMMENT '州/地区',
    sex                 STRING COMMENT '性别',
    general_health      STRING COMMENT '总体健康状况',
    physical_health_days INT COMMENT '过去30天身体不适天数',
    mental_health_days  INT COMMENT '过去30天心理不适天数',
    last_checkup_time   STRING COMMENT '最近一次体检时间',
    physical_activities_flag INT COMMENT '是否有身体活动(1=是,0=否)',
    sleep_hours         INT COMMENT '睡眠时长(小时)',
    removed_teeth        STRING COMMENT '拔牙情况',
    had_heart_attack_flag INT COMMENT '是否心梗/心脏病发作(1=是,0=否)',
    had_angina_flag     INT COMMENT '是否有心绞痛(1=是,0=否)',
    had_stroke_flag     INT COMMENT '是否有中风史(1=是,0=否)',
    had_asthma_flag     INT COMMENT '是否有哮喘(1=是,0=否)',
    had_skin_cancer_flag INT COMMENT '是否有皮肤癌(1=是,0=否)',
    had_copd_flag       INT COMMENT '是否有慢阻肺(1=是,0=否)',
    had_depressive_disorder_flag INT COMMENT '是否有抑郁障碍(1=是,0=否)',
    had_kidney_disease_flag INT COMMENT '是否有肾病(1=是,0=否)',
    had_arthritis_flag  INT COMMENT '是否有关节炎(1=是,0=否)',
    had_diabetes_text   STRING COMMENT '糖尿病原始值',
    had_diabetes_flag   INT COMMENT '糖尿病是否存在(1=是,0=否)',
    deaf_or_hard_of_hearing_flag INT COMMENT '是否耳聋/听力障碍(1=是,0=否)',
    blind_or_vision_difficulty_flag INT COMMENT '是否视觉障碍(1=是,0=否)',
    difficulty_concentrating_flag INT COMMENT '是否难以集中注意力(1=是,0=否)',
    difficulty_walking_flag INT COMMENT '是否行走困难(1=是,0=否)',
    difficulty_dressing_bathing_flag INT COMMENT '是否穿衣洗澡困难(1=是,0=否)',
    difficulty_errands_flag INT COMMENT '是否做日常事务困难(1=是,0=否)',
    smoker_status       STRING COMMENT '吸烟状态',
    ecigarette_usage    STRING COMMENT '电子烟使用情况',
    chest_scan_flag     INT COMMENT '是否做过胸部扫描(1=是,0=否)',
    race_ethnicity_category STRING COMMENT '种族/族裔',
    age_category        STRING COMMENT '年龄段',
    height_in_meters    DECIMAL(8,2) COMMENT '身高(米)',
    weight_in_kilograms DECIMAL(8,2) COMMENT '体重(千克)',
    bmi                 DECIMAL(6,2) COMMENT 'BMI',
    alcohol_drinkers_flag INT COMMENT '是否饮酒(1=是,0=否)',
    hiv_testing_flag    INT COMMENT '是否做过HIV检测(1=是,0=否)',
    flu_vax_last12_flag  INT COMMENT '是否接种流感疫苗(1=是,0=否)',
    pneumo_vax_ever_flag INT COMMENT '是否接种肺炎疫苗(1=是,0=否)',
    tetanus_last10_tdap_flag INT COMMENT '是否接种破伤风/Tdap(1=是,0=否)',
    high_risk_last_year_flag INT COMMENT '过去一年是否有高风险行为(1=是,0=否)',
    covid_pos_flag      INT COMMENT '是否新冠阳性(1=是,0=否)',
    load_dt             STRING COMMENT '装载日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE dwd_heart_2022_clean
SELECT
    'kaggle_2022' AS source_dataset,
    'heart_2022_raw.csv' AS source_file,
    CASE
        WHEN lower(trim(had_heart_attack)) = 'yes' OR lower(trim(had_angina)) = 'yes' THEN 1
        ELSE 0
    END AS risk_label,
    trim(state) AS state,
    trim(sex) AS sex,
    trim(general_health) AS general_health,
    CAST(NULLIF(trim(physical_health_days), '') AS INT) AS physical_health_days,
    CAST(NULLIF(trim(mental_health_days), '') AS INT) AS mental_health_days,
    trim(last_checkup_time) AS last_checkup_time,
    CASE WHEN lower(trim(physical_activities)) = 'yes' THEN 1 ELSE 0 END AS physical_activities_flag,
    CAST(NULLIF(trim(sleep_hours), '') AS INT) AS sleep_hours,
    trim(removed_teeth) AS removed_teeth,
    CASE WHEN lower(trim(had_heart_attack)) = 'yes' THEN 1 ELSE 0 END AS had_heart_attack_flag,
    CASE WHEN lower(trim(had_angina)) = 'yes' THEN 1 ELSE 0 END AS had_angina_flag,
    CASE WHEN lower(trim(had_stroke)) = 'yes' THEN 1 ELSE 0 END AS had_stroke_flag,
    CASE WHEN lower(trim(had_asthma)) = 'yes' THEN 1 ELSE 0 END AS had_asthma_flag,
    CASE WHEN lower(trim(had_skin_cancer)) = 'yes' THEN 1 ELSE 0 END AS had_skin_cancer_flag,
    CASE WHEN lower(trim(had_copd)) = 'yes' THEN 1 ELSE 0 END AS had_copd_flag,
    CASE WHEN lower(trim(had_depressive_disorder)) = 'yes' THEN 1 ELSE 0 END AS had_depressive_disorder_flag,
    CASE WHEN lower(trim(had_kidney_disease)) = 'yes' THEN 1 ELSE 0 END AS had_kidney_disease_flag,
    CASE WHEN lower(trim(had_arthritis)) = 'yes' THEN 1 ELSE 0 END AS had_arthritis_flag,
    trim(had_diabetes) AS had_diabetes_text,
    CASE
        WHEN lower(trim(had_diabetes)) LIKE 'yes%' THEN 1
        WHEN lower(trim(had_diabetes)) IN ('borderline diabetes', 'prediabetes') THEN 1
        ELSE 0
    END AS had_diabetes_flag,
    CASE WHEN lower(trim(deaf_or_hard_of_hearing)) = 'yes' THEN 1 ELSE 0 END AS deaf_or_hard_of_hearing_flag,
    CASE WHEN lower(trim(blind_or_vision_difficulty)) = 'yes' THEN 1 ELSE 0 END AS blind_or_vision_difficulty_flag,
    CASE WHEN lower(trim(difficulty_concentrating)) = 'yes' THEN 1 ELSE 0 END AS difficulty_concentrating_flag,
    CASE WHEN lower(trim(difficulty_walking)) = 'yes' THEN 1 ELSE 0 END AS difficulty_walking_flag,
    CASE WHEN lower(trim(difficulty_dressing_bathing)) = 'yes' THEN 1 ELSE 0 END AS difficulty_dressing_bathing_flag,
    CASE WHEN lower(trim(difficulty_errands)) = 'yes' THEN 1 ELSE 0 END AS difficulty_errands_flag,
    trim(smoker_status) AS smoker_status,
    trim(ecigarette_usage) AS ecigarette_usage,
    CASE WHEN lower(trim(chest_scan)) = 'yes' THEN 1 ELSE 0 END AS chest_scan_flag,
    trim(race_ethnicity_category) AS race_ethnicity_category,
    trim(age_category) AS age_category,
    CAST(NULLIF(trim(height_in_meters), '') AS DECIMAL(8,2)) AS height_in_meters,
    CAST(NULLIF(trim(weight_in_kilograms), '') AS DECIMAL(8,2)) AS weight_in_kilograms,
    CAST(NULLIF(trim(bmi), '') AS DECIMAL(6,2)) AS bmi,
    CASE WHEN lower(trim(alcohol_drinkers)) = 'yes' THEN 1 ELSE 0 END AS alcohol_drinkers_flag,
    CASE WHEN lower(trim(hiv_testing)) = 'yes' THEN 1 ELSE 0 END AS hiv_testing_flag,
    CASE WHEN lower(trim(flu_vax_last12)) = 'yes' THEN 1 ELSE 0 END AS flu_vax_last12_flag,
    CASE WHEN lower(trim(pneumo_vax_ever)) = 'yes' THEN 1 ELSE 0 END AS pneumo_vax_ever_flag,
    CASE WHEN lower(trim(tetanus_last10_tdap)) = 'yes' THEN 1 ELSE 0 END AS tetanus_last10_tdap_flag,
    CASE WHEN lower(trim(high_risk_last_year)) = 'yes' THEN 1 ELSE 0 END AS high_risk_last_year_flag,
    CASE WHEN lower(trim(covid_pos)) = 'yes' THEN 1 ELSE 0 END AS covid_pos_flag,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM ods_heart_2022_raw;

-- ---------------------------------------------------------
-- 3) UCI Cleveland 清洗表
-- ---------------------------------------------------------
DROP TABLE IF EXISTS dwd_uci_cleveland_clean;
CREATE TABLE dwd_uci_cleveland_clean (
    source_dataset      STRING COMMENT '数据来源名称',
    source_file         STRING COMMENT '原始文件名',
    risk_label          INT COMMENT '0=未患病/非风险,1=患病/有风险',
    age                 DECIMAL(5,1) COMMENT '年龄(岁)',
    sex_code            INT COMMENT '性别(1=男,0=女)',
    cp                  INT COMMENT '胸痛类型',
    trestbps            DECIMAL(6,1) COMMENT '静息血压',
    chol                DECIMAL(6,1) COMMENT '血清胆固醇',
    fbs_flag            INT COMMENT '空腹血糖是否大于120mg/dl',
    restecg             INT COMMENT '静息心电图结果',
    thalach             DECIMAL(6,1) COMMENT '最大心率',
    exang_flag          INT COMMENT '运动是否诱发心绞痛',
    oldpeak             DECIMAL(6,2) COMMENT 'ST 段压低程度',
    slope               INT COMMENT '峰值 ST 段斜率',
    ca                  INT COMMENT '主要血管数',
    thal                INT COMMENT '铊扫描结果',
    diagnosis_raw       INT COMMENT '原始诊断值 num',
    load_dt             STRING COMMENT '装载日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE dwd_uci_cleveland_clean
SELECT
    'uci_cleveland' AS source_dataset,
    'processed.cleveland.data' AS source_file,
    CASE WHEN CAST(trim(num) AS INT) > 0 THEN 1 ELSE 0 END AS risk_label,
    CAST(NULLIF(trim(age), '') AS DECIMAL(5,1)) AS age,
    CAST(NULLIF(trim(sex), '') AS INT) AS sex_code,
    CAST(NULLIF(trim(cp), '') AS INT) AS cp,
    CAST(NULLIF(trim(trestbps), '') AS DECIMAL(6,1)) AS trestbps,
    CAST(NULLIF(trim(chol), '') AS DECIMAL(6,1)) AS chol,
    CAST(NULLIF(trim(fbs), '') AS INT) AS fbs_flag,
    CAST(NULLIF(trim(restecg), '') AS INT) AS restecg,
    CAST(NULLIF(trim(thalach), '') AS DECIMAL(6,1)) AS thalach,
    CAST(NULLIF(trim(exang), '') AS INT) AS exang_flag,
    CAST(NULLIF(trim(oldpeak), '') AS DECIMAL(6,2)) AS oldpeak,
    CAST(NULLIF(trim(slope), '') AS INT) AS slope,
    CASE WHEN trim(ca) = '?' OR trim(ca) = '' THEN NULL ELSE CAST(trim(ca) AS INT) END AS ca,
    CASE WHEN trim(thal) = '?' OR trim(thal) = '' THEN NULL ELSE CAST(trim(thal) AS INT) END AS thal,
    CAST(NULLIF(trim(num), '') AS INT) AS diagnosis_raw,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM ods_uci_cleveland_raw;

-- ---------------------------------------------------------
-- 4) UCI 成本清洗表
-- ---------------------------------------------------------
DROP TABLE IF EXISTS dwd_uci_cost_clean;
CREATE TABLE dwd_uci_cost_clean (
    source_dataset      STRING COMMENT '数据来源名称',
    source_file         STRING COMMENT '原始文件名',
    feature             STRING COMMENT '检查项目名称',
    cost                DECIMAL(10,2) COMMENT '独立检查成本',
    cost_rank           INT COMMENT '按成本排序的名次',
    load_dt             STRING COMMENT '装载日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE dwd_uci_cost_clean
SELECT
    'uci_cost' AS source_dataset,
    'costs/heart-disease.cost' AS source_file,
    trim(feature) AS feature,
    CAST(trim(cost) AS DECIMAL(10,2)) AS cost,
    ROW_NUMBER() OVER (ORDER BY CAST(trim(cost) AS DECIMAL(10,2)) DESC, trim(feature)) AS cost_rank,
    date_format(current_date(), 'yyyy-MM-dd') AS load_dt
FROM ods_uci_cost_raw
WHERE trim(feature) <> '';

-- ---------------------------------------------------------
-- 5) 统一训练样本表
-- 说明：
-- - 适合导出给 Python 机器学习使用
-- - 将 Kaggle 2020 / 2022 / UCI Cleveland 的核心特征统一到一个宽表
-- ---------------------------------------------------------
DROP TABLE IF EXISTS dwd_heart_feature_sample;
CREATE TABLE dwd_heart_feature_sample (
    source_dataset      STRING COMMENT '数据来源名称',
    source_file         STRING COMMENT '原始文件名',
    risk_label          INT COMMENT '0=未患病/非风险,1=患病/有风险',
    age_band            STRING COMMENT '年龄段/年龄分组',
    sex_code            INT COMMENT '性别(1=男,0=女)',
    bmi                 DECIMAL(6,2) COMMENT 'BMI',
    physical_health_days INT COMMENT '身体不适天数',
    mental_health_days  INT COMMENT '心理不适天数',
    smoking_flag        INT COMMENT '吸烟标记',
    alcohol_flag        INT COMMENT '饮酒标记',
    activity_flag       INT COMMENT '身体活动标记',
    sleep_metric        DECIMAL(6,2) COMMENT '睡眠时长/小时',
    stroke_flag         INT COMMENT '中风史标记',
    diabetes_flag       INT COMMENT '糖尿病标记',
    kidney_flag         INT COMMENT '肾病标记',
    asthma_flag         INT COMMENT '哮喘标记',
    skin_cancer_flag    INT COMMENT '皮肤癌标记',
    chest_pain_type     INT COMMENT 'UCI 胸痛类型',
    resting_bp          DECIMAL(6,1) COMMENT '静息血压',
    cholesterol         DECIMAL(6,1) COMMENT '胆固醇',
    max_heart_rate      DECIMAL(6,1) COMMENT '最大心率',
    exercise_angina_flag INT COMMENT '运动诱发心绞痛标记',
    st_depression       DECIMAL(6,2) COMMENT 'ST 压低程度',
    slope               INT COMMENT 'ST 斜率',
    vessel_count        INT COMMENT '主要血管数',
    thal                INT COMMENT '铊扫描结果',
    load_dt             STRING COMMENT '装载日期'
)
STORED AS ORC;

INSERT OVERWRITE TABLE dwd_heart_feature_sample
SELECT
    source_dataset,
    source_file,
    risk_label,
    age_category AS age_band,
    sex_code,
    bmi,
    physical_health_days,
    mental_health_days,
    smoking_flag,
    alcohol_flag,
    physical_activity_flag AS activity_flag,
    CAST(sleep_time AS DECIMAL(6,2)) AS sleep_metric,
    stroke_flag,
    diabetic_flag AS diabetes_flag,
    kidney_disease_flag AS kidney_flag,
    asthma_flag,
    skin_cancer_flag,
    NULL AS chest_pain_type,
    NULL AS resting_bp,
    NULL AS cholesterol,
    NULL AS max_heart_rate,
    NULL AS exercise_angina_flag,
    NULL AS st_depression,
    NULL AS slope,
    NULL AS vessel_count,
    NULL AS thal,
    load_dt
FROM dwd_heart_2020_clean

UNION ALL

SELECT
    source_dataset,
    source_file,
    risk_label,
    age_category AS age_band,
    CASE WHEN lower(trim(sex)) = 'male' THEN 1 ELSE 0 END AS sex_code,
    bmi,
    physical_health_days,
    mental_health_days,
    CASE
        WHEN lower(trim(smoker_status)) LIKE '%former%' THEN 1
        WHEN lower(trim(smoker_status)) LIKE '%current%' THEN 1
        ELSE 0
    END AS smoking_flag,
    alcohol_drinkers_flag AS alcohol_flag,
    physical_activities_flag AS activity_flag,
    CAST(sleep_hours AS DECIMAL(6,2)) AS sleep_metric,
    had_stroke_flag AS stroke_flag,
    had_diabetes_flag AS diabetes_flag,
    had_kidney_disease_flag AS kidney_flag,
    had_asthma_flag AS asthma_flag,
    had_skin_cancer_flag AS skin_cancer_flag,
    NULL AS chest_pain_type,
    NULL AS resting_bp,
    NULL AS cholesterol,
    NULL AS max_heart_rate,
    NULL AS exercise_angina_flag,
    NULL AS st_depression,
    NULL AS slope,
    NULL AS vessel_count,
    NULL AS thal,
    load_dt
FROM dwd_heart_2022_clean

UNION ALL

SELECT
    source_dataset,
    source_file,
    risk_label,
    CASE
        WHEN age < 40 THEN 'Under 40'
        WHEN age < 50 THEN '40-49'
        WHEN age < 60 THEN '50-59'
        WHEN age < 70 THEN '60-69'
        ELSE '70+'
    END AS age_band,
    sex_code,
    NULL AS bmi,
    NULL AS physical_health_days,
    NULL AS mental_health_days,
    NULL AS smoking_flag,
    NULL AS alcohol_flag,
    NULL AS activity_flag,
    NULL AS sleep_metric,
    NULL AS stroke_flag,
    NULL AS diabetes_flag,
    NULL AS kidney_flag,
    NULL AS asthma_flag,
    NULL AS skin_cancer_flag,
    cp AS chest_pain_type,
    trestbps AS resting_bp,
    chol AS cholesterol,
    thalach AS max_heart_rate,
    exang_flag AS exercise_angina_flag,
    oldpeak AS st_depression,
    slope,
    ca AS vessel_count,
    thal,
    load_dt
FROM dwd_uci_cleveland_clean;
