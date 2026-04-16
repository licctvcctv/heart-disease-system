# 心脏病健康数据分析系统 API 契约

本文档定义 Vue3 前端与 Django REST Framework 后端之间的基础接口契约。分析接口必须读取 MySQL 中的离线 ADS 指标表；如果 ADS 数据缺失，应返回错误，而不是返回静态替代数据。

## 基础约定

- 基础路径：`/api`
- 响应格式：JSON
- 时间格式：ISO 8601 字符串
- 比例字段：除特别说明外，患病率、AUC 等使用 `0-1` 小数，前端负责格式化为百分比。
- 风险等级：
  - `low`：低风险
  - `medium`：中风险
  - `high`：高风险
- 分析接口数据源：MySQL 离线 ADS 表，包括 `ads_heart_overview`、`ads_heart_by_age`、`ads_heart_lifestyle`、`ads_heart_by_sex`、`ads_heart_by_bmi`、`ads_heart_comorbidity`、`ads_uci_clinical_risk`、`ads_model_metrics`、`ads_model_feature_importance`。

## 健康检查

`GET /api/health`

```json
{
  "ok": true,
  "service": "heart-disease-api",
  "version": "0.1.0",
  "time": "2026-04-15T19:30:00+08:00"
}
```

## 登录

`POST /api/auth/login`

请求：

```json
{
  "username": "admin",
  "password": "123456"
}
```

响应：

```json
{
  "token": "signed-token",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "nickname": "系统管理员"
  }
}
```

## 总览指标

`GET /api/dashboard/overview`

```json
{
  "sampleCount": 765230,
  "positiveCount": 67263,
  "negativeCount": 697967,
  "prevalenceRate": 0.0879,
  "datasetCount": 3,
  "modelAuc": 0.8207,
  "updatedAt": "2026-04-15T19:30:00+08:00",
  "datasets": [
    {
      "name": "Kaggle 2020 BRFSS",
      "rows": 319795,
      "columns": 18,
      "target": "HeartDisease",
      "usage": "主分析与模型训练"
    }
  ]
}
```

## 年龄维度分析

`GET /api/analysis/age`

```json
{
  "items": [
    {
      "ageGroup": "18-24",
      "sampleCount": 21064,
      "positiveCount": 130,
      "prevalenceRate": 0.0062
    }
  ]
}
```

## 生活方式分析

`GET /api/analysis/lifestyle`

```json
{
  "items": [
    {
      "factor": "Smoking",
      "category": "Yes",
      "sampleCount": 131908,
      "positiveCount": 16037,
      "prevalenceRate": 0.1216
    }
  ]
}
```

## UCI 临床指标分析

`GET /api/analysis/clinical`

```json
{
  "items": [
    {
      "feature": "cp",
      "label": "胸痛类型",
      "groups": [
        {
          "category": "typical angina",
          "sampleCount": 23,
          "positiveCount": 7,
          "prevalenceRate": 0.3043
        }
      ]
    }
  ]
}
```

## 模型指标

`GET /api/model/metrics`

```json
{
  "models": [
    {
      "name": "Logistic Regression",
      "accuracy": 0.91,
      "precision": 0.52,
      "recall": 0.68,
      "f1": 0.59,
      "auc": 0.84
    }
  ],
  "featureImportance": [
    {
      "feature": "GenHealth",
      "label": "总体健康状况",
      "importance": 0.21
    }
  ]
}
```

## 在线预测

`POST /api/predict`

请求：

```json
{
  "BMI": 28.4,
  "Smoking": "Yes",
  "AlcoholDrinking": "No",
  "Stroke": "No",
  "PhysicalHealth": 4,
  "MentalHealth": 2,
  "DiffWalking": "No",
  "Sex": "Male",
  "AgeCategory": "60-64",
  "Diabetic": "No",
  "PhysicalActivity": "Yes",
  "GenHealth": "Good",
  "SleepTime": 7,
  "Asthma": "No",
  "KidneyDisease": "No",
  "SkinCancer": "No"
}
```

响应：

```json
{
  "probability": 0.23,
  "riskLevel": "medium",
  "riskLabel": "中风险",
  "model": "Logistic Regression",
  "topFactors": [
    {
      "feature": "AgeCategory",
      "label": "年龄段",
      "impact": "60-64"
    }
  ],
  "createdAt": "2026-04-15T19:30:00+08:00"
}
```
