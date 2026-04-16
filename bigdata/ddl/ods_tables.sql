-- =========================================================
-- 心脏病健康数据分析系统
-- ODS 原始数据层建表脚本
-- 说明：
-- 1. 本脚本仅定义 Hive 表结构，不依赖当前机器已安装 Hive。
-- 2. ODS 层只负责“原样接入”，尽量保留源文件字段语义。
-- 3. Kaggle 2020 / 2022 以及 UCI Cleveland / UCI cost 均可在此层落地。
-- =========================================================

CREATE DATABASE IF NOT EXISTS heart_disease_system;
USE heart_disease_system;

-- ---------------------------------------------------------
-- 1) Kaggle 2020 原始数据
-- 文件：heart_2020_cleaned.csv
-- 字段：18 列，首行带表头
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ods_heart_2020_raw;
CREATE EXTERNAL TABLE ods_heart_2020_raw (
    heart_disease        STRING COMMENT 'HeartDisease: 是否患病(Yes/No)',
    bmi                  STRING COMMENT 'BMI: 体重指数',
    smoking              STRING COMMENT 'Smoking: 是否吸烟(Yes/No)',
    alcohol_drinking     STRING COMMENT 'AlcoholDrinking: 是否饮酒过量(Yes/No)',
    stroke               STRING COMMENT 'Stroke: 是否有中风史(Yes/No)',
    physical_health      STRING COMMENT 'PhysicalHealth: 过去30天身体不适天数',
    mental_health        STRING COMMENT 'MentalHealth: 过去30天心理不适天数',
    diff_walking         STRING COMMENT 'DiffWalking: 行走是否困难(Yes/No)',
    sex                  STRING COMMENT 'Sex: 性别',
    age_category         STRING COMMENT 'AgeCategory: 年龄段',
    race                 STRING COMMENT 'Race: 种族',
    diabetic             STRING COMMENT 'Diabetic: 糖尿病情况',
    physical_activity    STRING COMMENT 'PhysicalActivity: 是否有身体活动(Yes/No)',
    gen_health           STRING COMMENT 'GenHealth: 总体健康状况',
    sleep_time           STRING COMMENT 'SleepTime: 平均睡眠时长(小时)',
    asthma               STRING COMMENT 'Asthma: 是否哮喘(Yes/No)',
    kidney_disease       STRING COMMENT 'KidneyDisease: 是否肾病(Yes/No)',
    skin_cancer          STRING COMMENT 'SkinCancer: 是否皮肤癌(Yes/No)'
)
COMMENT 'Kaggle 2020 心脏病原始数据'
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    "separatorChar" = ",",
    "quoteChar" = "\"",
    "escapeChar" = "\\"
)
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- ---------------------------------------------------------
-- 2) Kaggle 2022 原始数据
-- 文件：heart_2022_no_nans.csv / heart_2022_with_nans.csv
-- 字段：40 列，可直接分别导入同一张 ODS 表
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ods_heart_2022_raw;
CREATE EXTERNAL TABLE ods_heart_2022_raw (
    state                    STRING COMMENT 'State: 州/地区',
    sex                      STRING COMMENT 'Sex: 性别',
    general_health           STRING COMMENT 'GeneralHealth: 总体健康状况',
    physical_health_days     STRING COMMENT 'PhysicalHealthDays: 过去30天身体不适天数',
    mental_health_days       STRING COMMENT 'MentalHealthDays: 过去30天心理不适天数',
    last_checkup_time        STRING COMMENT 'LastCheckupTime: 最近一次体检时间',
    physical_activities      STRING COMMENT 'PhysicalActivities: 是否有身体活动',
    sleep_hours              STRING COMMENT 'SleepHours: 睡眠时长(小时)',
    removed_teeth            STRING COMMENT 'RemovedTeeth: 拔牙情况',
    had_heart_attack         STRING COMMENT 'HadHeartAttack: 是否发生过心梗/心脏病发作',
    had_angina               STRING COMMENT 'HadAngina: 是否有心绞痛',
    had_stroke               STRING COMMENT 'HadStroke: 是否有中风史',
    had_asthma               STRING COMMENT 'HadAsthma: 是否有哮喘',
    had_skin_cancer          STRING COMMENT 'HadSkinCancer: 是否有皮肤癌',
    had_copd                 STRING COMMENT 'HadCOPD: 是否有慢阻肺',
    had_depressive_disorder  STRING COMMENT 'HadDepressiveDisorder: 是否有抑郁障碍',
    had_kidney_disease       STRING COMMENT 'HadKidneyDisease: 是否有肾病',
    had_arthritis            STRING COMMENT 'HadArthritis: 是否有关节炎',
    had_diabetes             STRING COMMENT 'HadDiabetes: 是否有糖尿病',
    deaf_or_hard_of_hearing  STRING COMMENT 'DeafOrHardOfHearing: 是否耳聋/听力障碍',
    blind_or_vision_difficulty STRING COMMENT 'BlindOrVisionDifficulty: 是否视觉障碍',
    difficulty_concentrating STRING COMMENT 'DifficultyConcentrating: 是否难以集中注意力',
    difficulty_walking       STRING COMMENT 'DifficultyWalking: 是否行走困难',
    difficulty_dressing_bathing STRING COMMENT 'DifficultyDressingBathing: 是否穿衣洗澡困难',
    difficulty_errands       STRING COMMENT 'DifficultyErrands: 是否做日常事务困难',
    smoker_status            STRING COMMENT 'SmokerStatus: 吸烟状态',
    ecigarette_usage         STRING COMMENT 'ECigaretteUsage: 电子烟使用情况',
    chest_scan               STRING COMMENT 'ChestScan: 是否做过胸部扫描',
    race_ethnicity_category  STRING COMMENT 'RaceEthnicityCategory: 种族/族裔',
    age_category             STRING COMMENT 'AgeCategory: 年龄段',
    height_in_meters         STRING COMMENT 'HeightInMeters: 身高(米)',
    weight_in_kilograms      STRING COMMENT 'WeightInKilograms: 体重(千克)',
    bmi                      STRING COMMENT 'BMI: 体重指数',
    alcohol_drinkers         STRING COMMENT 'AlcoholDrinkers: 是否饮酒',
    hiv_testing              STRING COMMENT 'HIVTesting: 是否做过HIV检测',
    flu_vax_last12           STRING COMMENT 'FluVaxLast12: 是否接种流感疫苗(过去12个月)',
    pneumo_vax_ever          STRING COMMENT 'PneumoVaxEver: 是否接种肺炎疫苗',
    tetanus_last10_tdap      STRING COMMENT 'TetanusLast10Tdap: 是否接种破伤风/Tdap',
    high_risk_last_year      STRING COMMENT 'HighRiskLastYear: 过去一年是否有高风险行为',
    covid_pos                STRING COMMENT 'CovidPos: 是否新冠阳性'
)
COMMENT 'Kaggle 2022 心脏病原始数据'
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    "separatorChar" = ",",
    "quoteChar" = "\"",
    "escapeChar" = "\\"
)
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- ---------------------------------------------------------
-- 3) UCI Cleveland 原始数据
-- 文件：processed.cleveland.data
-- 特点：无表头，14 个字段，缺失值以 ? 表示
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ods_uci_cleveland_raw;
CREATE EXTERNAL TABLE ods_uci_cleveland_raw (
    age         STRING COMMENT 'age: 年龄(岁)',
    sex         STRING COMMENT 'sex: 性别(1=男,0=女)',
    cp          STRING COMMENT 'cp: 胸痛类型',
    trestbps    STRING COMMENT 'trestbps: 静息血压',
    chol        STRING COMMENT 'chol: 血清胆固醇',
    fbs         STRING COMMENT 'fbs: 空腹血糖是否大于120mg/dl',
    restecg     STRING COMMENT 'restecg: 静息心电图结果',
    thalach     STRING COMMENT 'thalach: 最大心率',
    exang       STRING COMMENT 'exang: 运动是否诱发心绞痛',
    oldpeak     STRING COMMENT 'oldpeak: ST 段压低程度',
    slope       STRING COMMENT 'slope: 峰值 ST 段斜率',
    ca          STRING COMMENT 'ca: 主要血管数',
    thal        STRING COMMENT 'thal: 铊扫描结果',
    num         STRING COMMENT 'num: 诊断结果(0-4)'
)
COMMENT 'UCI Cleveland 原始数据'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

-- ---------------------------------------------------------
-- 4) UCI 成本原始数据
-- 文件：costs/heart-disease.cost
-- 格式：feature: cost
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ods_uci_cost_raw;
CREATE EXTERNAL TABLE ods_uci_cost_raw (
    feature     STRING COMMENT '检查项目名称',
    cost        STRING COMMENT '独立检查成本'
)
COMMENT 'UCI 心脏病检查成本原始数据'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ':'
COLLECTION ITEMS TERMINATED BY ','
STORED AS TEXTFILE;
