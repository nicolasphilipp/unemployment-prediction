-- ============================================================
-- VIEW DEFINITIONS for Unemployment Prediction ML Pipeline
-- Vienna Districts: Unemployment & Tourism Data (2002–present)
-- ============================================================

-- VIEW 1: ml_feature_table
-- Purpose: Main feature table for the ML pipeline.
-- Joins unemployment and tourism data on district and year,
-- filtered to total unemployment (SEX=0) to avoid duplication.
-- Exposes all numeric predictors and the target variable (UEP_VALUE).
-- ============================================================
CREATE VIEW ml_feature_table AS
SELECT
    u.DISTRICT_CODE,
    u.REF_YEAR,
    u.UEP_VALUE        AS unemployment_count,
    u.UEP_DENSITY      AS unemployment_per_1000,
    t.TOU_VALUE        AS overnight_stays,
    t.TOU_DENSITY      AS overnight_stays_per_1000,
    t.POP_AVE          AS avg_population
FROM unemployment u
INNER JOIN tourism t
    ON  u.DISTRICT_CODE = t.DISTRICT_CODE
    AND u.REF_YEAR      = t.REF_YEAR
WHERE u.SEX = 0;  -- 0 = total (avoids duplicate rows for men/women)


-- VIEW 2: ml_feature_table_by_gender
-- Purpose: Gender-disaggregated feature table.
-- Useful for experiments that include SEX as a feature.
-- Exposes SEX (1=men, 2=women) alongside all numeric predictors.
-- ============================================================
CREATE VIEW ml_feature_table_by_gender AS
SELECT
    u.DISTRICT_CODE,
    u.REF_YEAR,
    u.SEX,
    u.UEP_VALUE        AS unemployment_count,
    u.UEP_DENSITY      AS unemployment_per_1000,
    t.TOU_VALUE        AS overnight_stays,
    t.TOU_DENSITY      AS overnight_stays_per_1000,
    t.POP_AVE          AS avg_population
FROM unemployment u
INNER JOIN tourism t
    ON  u.DISTRICT_CODE = t.DISTRICT_CODE
    AND u.REF_YEAR      = t.REF_YEAR
WHERE u.SEX IN (1, 2);


-- VIEW 3: district_yearly_aggregates
-- Purpose: Aggregated statistics per district across all years.
-- Useful for exploratory analysis and feature engineering
-- (e.g. computing baseline unemployment levels per district).
-- ============================================================
CREATE VIEW district_yearly_aggregates AS
SELECT
    u.DISTRICT_CODE,
    u.REF_YEAR,
    AVG(u.UEP_VALUE)   AS avg_unemployment_count,
    AVG(u.UEP_DENSITY) AS avg_unemployment_per_1000,
    AVG(t.TOU_VALUE)   AS avg_overnight_stays,
    AVG(t.TOU_DENSITY) AS avg_overnight_stays_per_1000,
    AVG(t.POP_AVE)     AS avg_population
FROM unemployment u
INNER JOIN tourism t
    ON  u.DISTRICT_CODE = t.DISTRICT_CODE
    AND u.REF_YEAR      = t.REF_YEAR
WHERE u.SEX = 0
GROUP BY u.DISTRICT_CODE, u.REF_YEAR;


-- VIEW 4: train_split
-- Purpose: Training set for the ML pipeline (2002–2019).
-- Chronological split — earlier years used for training
-- to prevent data leakage from future observations.
-- ============================================================
CREATE VIEW train_split AS
SELECT *
FROM ml_feature_table
WHERE REF_YEAR BETWEEN 2002 AND 2019;


-- VIEW 5: validation_split
-- Purpose: Validation set (2020–2021).
-- Used for hyperparameter tuning during model development.
-- ============================================================
CREATE VIEW validation_split AS
SELECT *
FROM ml_feature_table
WHERE REF_YEAR BETWEEN 2020 AND 2021;


-- VIEW 6: test_split
-- Purpose: Test set (2022–present).
-- Held out entirely until final model evaluation.
-- ============================================================
CREATE VIEW test_split AS
SELECT *
FROM ml_feature_table
WHERE REF_YEAR >= 2022;
