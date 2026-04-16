CREATE TABLE IF NOT EXISTS ads_heart_overview (
    dataset_name VARCHAR(64) NOT NULL,
    sample_count BIGINT NOT NULL,
    positive_count BIGINT NOT NULL,
    negative_count BIGINT NOT NULL,
    prevalence_rate DECIMAL(8,4) NOT NULL,
    source_file VARCHAR(255),
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_heart_by_age (
    dataset_name VARCHAR(64) NOT NULL,
    age_band VARCHAR(64),
    sample_count BIGINT NOT NULL,
    positive_count BIGINT NOT NULL,
    prevalence_rate DECIMAL(8,4) NOT NULL,
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_heart_by_sex (
    dataset_name VARCHAR(64) NOT NULL,
    sex_code INT,
    sex_label VARCHAR(32),
    sample_count BIGINT NOT NULL,
    positive_count BIGINT NOT NULL,
    prevalence_rate DECIMAL(8,4) NOT NULL,
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_heart_by_bmi (
    dataset_name VARCHAR(64) NOT NULL,
    bmi_group VARCHAR(64),
    sample_count BIGINT NOT NULL,
    positive_count BIGINT NOT NULL,
    prevalence_rate DECIMAL(8,4) NOT NULL,
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_heart_lifestyle (
    dataset_name VARCHAR(64) NOT NULL,
    factor_name VARCHAR(64) NOT NULL,
    factor_value VARCHAR(64),
    sample_count BIGINT NOT NULL,
    positive_count BIGINT NOT NULL,
    prevalence_rate DECIMAL(8,4) NOT NULL,
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_heart_comorbidity (
    dataset_name VARCHAR(64) NOT NULL,
    disease_name VARCHAR(64) NOT NULL,
    disease_flag INT,
    sample_count BIGINT NOT NULL,
    positive_count BIGINT NOT NULL,
    prevalence_rate DECIMAL(8,4) NOT NULL,
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_uci_clinical_risk (
    feature_name VARCHAR(64) NOT NULL,
    feature_label VARCHAR(128),
    feature_value VARCHAR(128),
    sample_count BIGINT NOT NULL,
    positive_count BIGINT NOT NULL,
    prevalence_rate DECIMAL(8,4) NOT NULL,
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_uci_cost_analysis (
    feature VARCHAR(128) NOT NULL,
    cost DECIMAL(10,2),
    cost_rank INT,
    cost_level VARCHAR(32),
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_model_metrics (
    model_name VARCHAR(128) NOT NULL,
    accuracy DECIMAL(8,4),
    precision_score DECIMAL(8,4),
    recall_score DECIMAL(8,4),
    f1_score DECIMAL(8,4),
    auc DECIMAL(8,4),
    train_dataset VARCHAR(64),
    note VARCHAR(255),
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ads_model_feature_importance (
    model_name VARCHAR(128) NOT NULL,
    feature_name VARCHAR(128) NOT NULL,
    feature_label VARCHAR(128),
    importance DECIMAL(12,6),
    train_dataset VARCHAR(64),
    load_dt VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
