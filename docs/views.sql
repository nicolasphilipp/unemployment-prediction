-- ============================================================
-- VIEW DEFINITIONS for Unemployment Prediction ML Pipeline
-- Vienna Districts: Unemployment & Tourism Data (2002–present)
--
-- Schema (3NF):
--   district         (district_id PK, nuts_code, district_code)
--   measurement_info (measurement_id UNIQUE, district_id FK,
--                     reference_date, population_avg)
--   unemployment     (measurement_id FK, gender, value, density)
--   tourism          (measurement_id FK, value, density)
-- ============================================================


-- VIEW 1: ml_feature_table
-- Purpose: Main denormalized feature table for the ML pipeline.
--   Joins all four tables on measurement_id and district_id.
--   Filters to gender = 'Both' to avoid row duplication.
--   Excludes district 90000 (Vienna-wide total aggregate).
--   Excludes COVID outlier years 2020 and 2021.
--   This view is the base for all train/val/test split views.
-- ============================================================
CREATE VIEW ml_feature_table AS
SELECT
    d.district_code                 AS district_code,
    YEAR(mi.reference_date)         AS ref_year,
    mi.population_avg               AS population_avg,
    u.value                         AS uep_value,
    u.density                       AS uep_density,
    t.value                         AS tou_value,
    t.density                       AS tou_density
FROM measurement_info mi
JOIN district     d ON  d.district_id    = mi.district_id
JOIN unemployment u ON  u.measurement_id = mi.measurement_id
JOIN tourism      t ON  t.measurement_id = mi.measurement_id
WHERE u.gender          = 'Both'
  AND d.district_code   != 90000
  AND YEAR(mi.reference_date) NOT IN (2020, 2021);


-- VIEW 2: train_split
-- Purpose: Training portion of the chronological data split.
--   Covers years 2002–2015 (322 expected rows).
--   Used to fit both Linear Regression and Random Forest models.
-- ============================================================
CREATE VIEW train_split AS
SELECT *
FROM ml_feature_table
WHERE ref_year <= 2015;


-- VIEW 3: validation_split
-- Purpose: Validation portion of the chronological data split.
--   Covers years 2016–2018 (69 expected rows).
--   Used for hyperparameter tuning during model development.
-- ============================================================
CREATE VIEW validation_split AS
SELECT *
FROM ml_feature_table
WHERE ref_year BETWEEN 2016 AND 2018;


-- VIEW 4: test_split
-- Purpose: Test portion of the chronological data split.
--   Covers years 2019+ (69 expected rows; 2020–2021 already
--   excluded in ml_feature_table base view).
--   Held out entirely until final model evaluation.
-- ============================================================
CREATE VIEW test_split AS
SELECT *
FROM ml_feature_table
WHERE ref_year >= 2019;


-- VIEW 5: district_yearly_aggregates
-- Purpose: Per-district yearly aggregations for EDA and
--   baseline feature engineering.
--   Exposes average unemployment and tourism metrics grouped
--   by district and year, useful for trend analysis.
-- ============================================================
CREATE VIEW district_yearly_aggregates AS
SELECT
    d.district_code                  AS district_code,
    YEAR(mi.reference_date)          AS ref_year,
    mi.population_avg                AS population_avg,
    AVG(u.value)                     AS avg_uep_value,
    AVG(u.density)                   AS avg_uep_density,
    AVG(t.value)                     AS avg_tou_value,
    AVG(t.density)                   AS avg_tou_density
FROM measurement_info mi
JOIN district     d ON  d.district_id    = mi.district_id
JOIN unemployment u ON  u.measurement_id = mi.measurement_id
JOIN tourism      t ON  t.measurement_id = mi.measurement_id
WHERE u.gender        = 'Both'
  AND d.district_code != 90000
GROUP BY d.district_code, YEAR(mi.reference_date), mi.population_avg;


-- VIEW 6: gender_disaggregated_features
-- Purpose: Gender-disaggregated feature table (male/female).
--   Includes GENDER column for experiments that incorporate
--   sex as an additional predictor variable.
--   Excludes COVID years and Vienna-wide total.
-- ============================================================
CREATE VIEW gender_disaggregated_features AS
SELECT
    d.district_code                  AS district_code,
    YEAR(mi.reference_date)          AS ref_year,
    mi.population_avg                AS population_avg,
    u.gender                         AS gender,
    u.value                          AS uep_value,
    u.density                        AS uep_density,
    t.value                          AS tou_value,
    t.density                        AS tou_density
FROM measurement_info mi
JOIN district     d ON  d.district_id    = mi.district_id
JOIN unemployment u ON  u.measurement_id = mi.measurement_id
JOIN tourism      t ON  t.measurement_id = mi.measurement_id
WHERE u.gender IN ('Male', 'Female')
  AND d.district_code  != 90000
  AND YEAR(mi.reference_date) NOT IN (2020, 2021);
