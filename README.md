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
