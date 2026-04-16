# 心脏病健康数据分析系统数据字典

本文档整理系统中用于 Hive 分层、Python 训练和前端展示的关键字段。口径已统一为 `risk_label`：

- `0` = 未患病 / 非风险
- `1` = 患病 / 有风险

## 1. 统一目标字段

| 字段 | 英文含义 | 中文含义 | 目标字段 | 用途 |
| --- | --- | --- | --- | --- |
| `risk_label` | unified risk label | 统一风险标签 | 是 | 统一训练、统计、前端展示口径 |
| `source_dataset` | source dataset | 数据来源 | 否 | 区分 Kaggle 2020 / 2022 / UCI Cleveland |
| `source_file` | source file | 原始文件名 | 否 | 追溯导入来源 |

## 2. Kaggle 2020 关键字段

| 字段 | 英文含义 | 中文含义 | 目标字段 | 用途 |
| --- | --- | --- | --- | --- |
| `HeartDisease` | heart disease | 是否患心脏病 | `risk_label` | 目标标签来源 |
| `BMI` | body mass index | 体重指数 | `bmi` | 风险分析与模型特征 |
| `Smoking` | smoking | 是否吸烟 | `smoking_flag` | 生活方式分析 |
| `AlcoholDrinking` | alcohol drinking | 是否饮酒过量 | `alcohol_flag` | 生活方式分析 |
| `Stroke` | stroke history | 是否有中风史 | `stroke_flag` | 共病分析 |
| `PhysicalHealth` | physical health days | 身体不适天数 | `physical_health_days` | 健康状态分析 |
| `MentalHealth` | mental health days | 心理不适天数 | `mental_health_days` | 健康状态分析 |
| `DiffWalking` | difficulty walking | 行走是否困难 | `diff_walking_flag` | 功能受限分析 |
| `Sex` | sex | 性别 | `sex_code` | 人群维度分析 |
| `AgeCategory` | age category | 年龄段 | `age_category` | 人群维度分析 |
| `Race` | race | 种族 | `race` | 人群分布分析 |
| `Diabetic` | diabetic status | 糖尿病情况 | `diabetic_flag` | 共病分析 |
| `PhysicalActivity` | physical activity | 是否有身体活动 | `activity_flag` | 生活方式分析 |
| `GenHealth` | general health | 总体健康状况 | `gen_health` | 健康评分分析 |
| `SleepTime` | sleep time | 睡眠时长 | `sleep_time` | 生活方式分析 |
| `Asthma` | asthma | 是否哮喘 | `asthma_flag` | 共病分析 |
| `KidneyDisease` | kidney disease | 是否肾病 | `kidney_disease_flag` | 共病分析 |
| `SkinCancer` | skin cancer | 是否皮肤癌 | `skin_cancer_flag` | 共病分析 |

## 3. Kaggle 2022 关键字段

| 字段 | 英文含义 | 中文含义 | 目标字段 | 用途 |
| --- | --- | --- | --- | --- |
| `HadHeartAttack` | had heart attack | 是否发生过心梗/心脏病发作 | `risk_label` | 目标标签来源 |
| `HadAngina` | had angina | 是否有心绞痛 | `risk_label` | 目标标签补充来源 |
| `State` | state | 州/地区 | `state` | 地域分析 |
| `Sex` | sex | 性别 | `sex` | 人群维度分析 |
| `GeneralHealth` | general health | 总体健康状况 | `general_health` | 健康状态分析 |
| `PhysicalHealthDays` | physical health days | 身体不适天数 | `physical_health_days` | 健康状态分析 |
| `MentalHealthDays` | mental health days | 心理不适天数 | `mental_health_days` | 健康状态分析 |
| `LastCheckupTime` | last checkup time | 最近一次体检时间 | `last_checkup_time` | 就医行为分析 |
| `PhysicalActivities` | physical activities | 是否有身体活动 | `physical_activities_flag` | 生活方式分析 |
| `SleepHours` | sleep hours | 睡眠时长 | `sleep_hours` | 生活方式分析 |
| `RemovedTeeth` | removed teeth | 拔牙情况 | `removed_teeth` | 口腔健康辅助分析 |
| `HadStroke` | had stroke | 是否有中风史 | `had_stroke_flag` | 共病分析 |
| `HadAsthma` | had asthma | 是否有哮喘 | `had_asthma_flag` | 共病分析 |
| `HadSkinCancer` | had skin cancer | 是否有皮肤癌 | `had_skin_cancer_flag` | 共病分析 |
| `HadCOPD` | had COPD | 是否有慢阻肺 | `had_copd_flag` | 共病分析 |
| `HadDepressiveDisorder` | depressive disorder | 是否有抑郁障碍 | `had_depressive_disorder_flag` | 精神健康分析 |
| `HadKidneyDisease` | had kidney disease | 是否有肾病 | `had_kidney_disease_flag` | 共病分析 |
| `HadArthritis` | had arthritis | 是否有关节炎 | `had_arthritis_flag` | 共病分析 |
| `HadDiabetes` | had diabetes | 是否有糖尿病 | `had_diabetes_flag` | 共病分析 |
| `SmokerStatus` | smoker status | 吸烟状态 | `smoker_status` | 生活方式分析 |
| `ECigaretteUsage` | e-cigarette usage | 电子烟使用情况 | `ecigarette_usage` | 生活方式分析 |
| `ChestScan` | chest scan | 是否做过胸部扫描 | `chest_scan_flag` | 检查行为分析 |
| `RaceEthnicityCategory` | race/ethnicity category | 种族/族裔 | `race_ethnicity_category` | 人群维度分析 |
| `AgeCategory` | age category | 年龄段 | `age_category` | 人群维度分析 |
| `HeightInMeters` | height in meters | 身高(米) | `height_in_meters` | 计算 BMI / 特征工程 |
| `WeightInKilograms` | weight in kilograms | 体重(千克) | `weight_in_kilograms` | 计算 BMI / 特征工程 |
| `BMI` | body mass index | 体重指数 | `bmi` | 风险分析与模型特征 |
| `AlcoholDrinkers` | alcohol drinkers | 是否饮酒 | `alcohol_drinkers_flag` | 生活方式分析 |
| `HIVTesting` | HIV testing | 是否做过 HIV 检测 | `hiv_testing_flag` | 检查行为分析 |
| `FluVaxLast12` | flu vaccine last 12 months | 是否接种流感疫苗 | `flu_vax_last12_flag` | 预防行为分析 |
| `PneumoVaxEver` | pneumonia vaccine ever | 是否接种肺炎疫苗 | `pneumo_vax_ever_flag` | 预防行为分析 |
| `TetanusLast10Tdap` | tetanus last 10 years | 是否接种破伤风/Tdap | `tetanus_last10_tdap_flag` | 预防行为分析 |
| `HighRiskLastYear` | high risk last year | 过去一年是否有高风险行为 | `high_risk_last_year_flag` | 行为风险分析 |
| `CovidPos` | COVID positive | 是否新冠阳性 | `covid_pos_flag` | 疫情影响辅助分析 |

## 4. UCI Cleveland 关键字段

| 字段 | 英文含义 | 中文含义 | 目标字段 | 用途 |
| --- | --- | --- | --- | --- |
| `num` | diagnosis of heart disease | 诊断结果 | `risk_label` | 二分类目标来源，`num > 0` 记为 1 |
| `age` | age | 年龄 | `age` | 年龄分析 |
| `sex` | sex | 性别 | `sex_code` | 人群分析 |
| `cp` | chest pain type | 胸痛类型 | `cp` | 核心临床特征 |
| `trestbps` | resting blood pressure | 静息血压 | `trestbps` | 核心临床特征 |
| `chol` | serum cholesterol | 血清胆固醇 | `chol` | 核心临床特征 |
| `fbs` | fasting blood sugar > 120 | 空腹血糖是否超标 | `fbs_flag` | 风险分析 |
| `restecg` | resting ECG result | 静息心电图结果 | `restecg` | 核心临床特征 |
| `thalach` | maximum heart rate achieved | 最大心率 | `thalach` | 核心临床特征 |
| `exang` | exercise induced angina | 运动是否诱发心绞痛 | `exang_flag` | 核心临床特征 |
| `oldpeak` | ST depression induced by exercise | ST 压低程度 | `oldpeak` | 核心临床特征 |
| `slope` | slope of peak exercise ST segment | ST 斜率 | `slope` | 核心临床特征 |
| `ca` | number of major vessels | 主要血管数 | `ca` | 核心临床特征 |
| `thal` | thalassemia scan result | 铊扫描结果 | `thal` | 核心临床特征 |

## 5. UCI 成本字段

| 字段 | 英文含义 | 中文含义 | 目标字段 | 用途 |
| --- | --- | --- | --- | --- |
| `feature` | feature name | 检查项目名称 | 否 | 成本分析维度 |
| `cost` | independent test cost | 独立检查成本 | 否 | 成本对比分析 |
| `cost_rank` | cost rank | 成本排名 | 否 | 高低成本排序 |

## 6. DWD 统一训练样本字段

`dwd_heart_feature_sample` 是 Python 机器学习最适合读取的统一特征表，字段语义如下：

| 字段 | 英文含义 | 中文含义 | 目标字段 | 用途 |
| --- | --- | --- | --- | --- |
| `age_band` | age band | 年龄分组 | 否 | 统一年龄粒度 |
| `sex_code` | sex code | 性别编码 | 否 | 统一数值特征 |
| `bmi` | body mass index | 体重指数 | 否 | 模型特征 |
| `physical_health_days` | physical health days | 身体不适天数 | 否 | 模型特征 |
| `mental_health_days` | mental health days | 心理不适天数 | 否 | 模型特征 |
| `smoking_flag` | smoking flag | 吸烟标记 | 否 | 模型特征 |
| `alcohol_flag` | alcohol flag | 饮酒标记 | 否 | 模型特征 |
| `activity_flag` | activity flag | 身体活动标记 | 否 | 模型特征 |
| `sleep_metric` | sleep metric | 睡眠时长 | 否 | 模型特征 |
| `stroke_flag` | stroke flag | 中风标记 | 否 | 模型特征 |
| `diabetes_flag` | diabetes flag | 糖尿病标记 | 否 | 模型特征 |
| `kidney_flag` | kidney flag | 肾病标记 | 否 | 模型特征 |
| `asthma_flag` | asthma flag | 哮喘标记 | 否 | 模型特征 |
| `chest_pain_type` | chest pain type | 胸痛类型 | 否 | UCI 临床特征 |
| `resting_bp` | resting blood pressure | 静息血压 | 否 | UCI 临床特征 |
| `cholesterol` | cholesterol | 胆固醇 | 否 | UCI 临床特征 |
| `max_heart_rate` | max heart rate | 最大心率 | 否 | UCI 临床特征 |
| `exercise_angina_flag` | exercise angina flag | 运动诱发心绞痛标记 | 否 | UCI 临床特征 |
| `st_depression` | ST depression | ST 压低程度 | 否 | UCI 临床特征 |
| `slope` | slope | ST 斜率 | 否 | UCI 临床特征 |
| `vessel_count` | vessel count | 主要血管数 | 否 | UCI 临床特征 |
| `thal` | thal | 铊扫描结果 | 否 | UCI 临床特征 |

## 7. 字段使用建议

- 做大屏总览：优先用 `risk_label`、`source_dataset`、`age_band`、`sex_code`
- 做生活方式分析：优先用 `smoking_flag`、`alcohol_flag`、`activity_flag`、`sleep_metric`
- 做共病分析：优先用 `stroke_flag`、`diabetes_flag`、`kidney_flag`、`asthma_flag`
- 做 UCI 临床分析：优先用 `cp`、`trestbps`、`chol`、`thalach`、`exang_flag`、`oldpeak`、`slope`、`ca`、`thal`
- 做机器学习训练：优先读取 `dwd_heart_feature_sample`

