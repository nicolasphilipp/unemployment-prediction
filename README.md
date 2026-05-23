# Prediction of unemployment in Vienna districts using tourism and demographic data

## What is it about?

The aim of the experiment is to predict unemployment levels in the districts of Vienna by using tourism (overnight stays) and population data. As tourism is an important economic sector, it can influence employment levels in areas with higher visitor activity. By applying machine learning techniques to open government data, the experiment aims to determine if overnight stays and population are useful predictors for unemployment levels.

## Used datasets

The experiment uses two datasets from the Austrian Open Government Data portal:

### 1. Unemployed Persons Since 2002 - Districts of Vienna

(Stadt Wien - Wirtschaft und Finanzen, _Arbeitslos gemeldete Personen im Alter 15-64 Jahre nach Geschlecht (absolut und pro 1.000 EinwohnerInnen) im Jahresdurchschnitt seit 2002 - Bezirke Wien_, Open Government Data Austria, Dataset ID: 9462d680-ede9-40b9-8102-b9baebaa4fbb. Available at: https://www.data.gv.at/katalog/dataset/9462d680-ede9-40b9-8102-b9baebaa4fbb, 2025)

**Features:**

- `NUTS`: statistical region of Austria (always "AT13" for Vienna)
- `DISTRICT_CODE`: municipality code
- `SUB_DISTRICT_CODE`: census district code (same as municipality code in the granularity of this dataset)
- `REF_YEAR`: reference year
- `REF_DATE`: reference date
- `SEX`: 0 = total, 1 = men, 2 = women
- `UEP_VALUE`: average number of unemployed persons (age 15-64)
- `UEP_DENSITY`: unemployed persons per 1,000 inhabitants

### 2. Guest Overnight Stays Since 2002 - Districts of Vienna

(Stadt Wien - Wirtschaft und Finanzen, _Gästeübernachtungen (absolut und pro 1.000 EinwohnerInnen) seit 2002 - Bezirke Wien_, Open Government Data Austria, Dataset ID: ae4ebf87-9f46-4f05-9e3d-dbff002b216d. Available at: https://www.data.gv.at/katalog/datasets/ae4ebf87-9f46-4f05-9e3d-dbff002b216d, 2025)

**Features:**

- `NUTS`: statistical region of Austria (always "AT13" for Vienna)
- `DISTRICT_CODE`: municipality code
- `SUB_DISTRICT_CODE`: census district code (same as municipality code in the granularity of this dataset)
- `REF_YEAR`: reference year
- `REF_DATE`: reference date
- `TOU_VALUE`: total guest overnight stays
- `TOU_DENSITY`: overnight stays per 1,000 inhabitants
- `POP_AVE`: average population

## Database Schema & Views (DBRepo)

The experiment data is stored in a relational database (3NF) on the TU Wien DBRepo test instance. SQL views de-normalize the schema into query-ready formats for the ML pipeline.

### Database Access

- **DBRepo Instance**: https://test.dbrepo.tuwien.ac.at
- **Database ID**: `412fb0ce-5299-4d0e-a271-4641b1365b8a`
- **Persistent Identifier**: [https://doi.org/10.82556/n73d-ks38](https://doi.org/10.82556/n73d-ks38)

### Schema Overview (3NF)

The database follows Third Normal Form with four tables:

| Table              | Description                                     | Foreign Key                                           |
| ------------------ | ----------------------------------------------- | ----------------------------------------------------- |
| `district`         | Vienna district identifiers and NUTS codes      | `district_id` (PK)                                    |
| `measurement_info` | Temporal and district metadata for measurements | `district_id` → `district`, `measurement_id` (UNIQUE) |
| `unemployment`     | Unemployment statistics by gender               | `measurement_id` → `measurement_info`                 |
| `tourism`          | Tourism overnight stay statistics               | `measurement_id` → `measurement_info`                 |

### SQL Views for ML Pipeline

The following views de-normalize the schema to support the machine learning workflow. All views are defined in [`docs/views.sql`](docs/views.sql) and implemented in the DBRepo instance.

#### Base Feature View

| View Name          | Purpose                                                                                                                                               | Key Columns                                                                         |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `ml_feature_table` | Main denormalized feature table joining all sources. Filters: gender='TOTAL', excludes district 90000 (Vienna total), excludes COVID years 2020-2021. | `district_code`, `ref_year`, `uep_value`, `uep_density`, `tou_value`, `tou_density` |

#### Data Split Views (Chronological)

| View Name          | Purpose                                   | Time Range | Expected Rows |
| ------------------ | ----------------------------------------- | ---------- | ------------- |
| `train_split`      | Training data for model fitting           | 2002-2015  | ~322          |
| `validation_split` | Validation data for hyperparameter tuning | 2016-2018  | ~69           |
| `test_split`       | Test data for final evaluation            | 2019+      | ~69           |

#### Analytical Views

| View Name                       | Purpose                                                                                                               | Use Case                                                                  |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `inner_city_districts`          | Feature table restricted to the nine inner-city districts (90100-90900) with disproportionately high tourism activity | District-segment-specific models and inner-city vs. outer-district EDA    |
| `outer_city_districts`          | Feature table restricted to the fourteen outer residential districts (91000-92300) with lower tourism density         | District-segment-specific models and comparison against inner-city trends |
| `gender_disaggregated_features` | Gender-specific data for models using sex as predictor (Male/Female only, excludes Both)                              | Advanced modeling experiments                                             |

### Important Notes

- **Gender values**: The `unemployment` table uses enum values: `'Both'`, `'Male'`, `'Female'`.
- **COVID exclusion**: Years 2020 and 2021 are excluded from all views as outliers (pandemic effect on tourism).

### View Definitions Location

- **SQL source**: [`docs/views.sql`](docs/views.sql)
- **Live views**: https://test.dbrepo.tuwien.ac.at/database/412fb0ce-5299-4d0e-a271-4641b1365b8a/view

## File organisation

This project follows a consistent file naming convention to improve clarity, reproducibility, and ease of collaboration. The structure is organised into dedicated directories based on file purpose.

```
config/
data/
docs/
outputs/
  ├── figures/
  └── models/
src/
```

### 1. Data (`data/`)

All datasets (raw and processed) are stored in the `data/` directory.

Naming Pattern:

`<source>_<description>_<version>.<extension>`

Examples:

- `vienna_unemployment_since_2002_raw_v1.0.csv`
- `vienna_tourism_since_2002_raw_v1.0.csv`

### 2. Documentation (`docs/`)

Project-related documentation is stored in the `docs/` directory.

Naming pattern:

`<topic>_<description>.<extension>`

Example:

- `dmp_prediction_of_unemployment_in_vienna_districts_using_tourism_and_demographic_data.pdf`

### 3. Outputs (`outputs/`)

#### a) Figures (`outputs/figures/`)

All generated plots and visualisations are stored here.

Naming pattern:

`fig_<topic>_<detail>_<version>.<extension>`

Examples:

- `fig_unemployment_tourism_over_time_v1.0.png`
- `fig_unemployment_tourism_per_district_v1.0.png`

#### b) Model artefacts (`outputs/models/`)

Trained models and related artefacts are stored here.

Naming pattern:

`model_<algorithm>_<version>.<extension>`

Examples:

- `model_random_forest_v1.0.pkl`

### 3. Source code (`src/`)

All source code is contained in the `src/` directory. In this project, the primary source file is a Jupyter notebook (`src/unemployment_prediction.ipynb`). If more scripts are added, they should adhere to the naming pattern and use numeric prefixes to indicate workflow order.

Naming pattern:

`<step>_<task_description>.<extension>`

Examples:

- `01_data_preparation.py`
- `02_exploratory_analysis.py`

### 4. Configuration files (`config/`)

Configuration files define parameters and settings.

Naming pattern:

`config_<purpose>.<extension>`

Example:

- `config_general.yaml`

## General naming conventions

- Use lowercase letters and underscores (`_`) only
- Avoid spaces and special characters
- Keep names descriptive but concise
- Use versioning (`v1.0`, `v2.0`, ...) for datasets, figures, and models
- Ensure naming consistency across all directories
