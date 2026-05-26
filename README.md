# Prediction of Unemployment in Vienna Districts Using Tourism and Demographic Data

[![DOI](https://zenodo.org/badge/1226524836.svg)](https://doi.org/10.5281/zenodo.20395175)

## Abstract

This experiment investigates whether tourism activity and population size can serve as useful predictors of unemployment levels across the 23 districts of Vienna. Using open government data from the Austrian Open Government Data portal (data.gv.at) covering the years 2002-2019 (with COVID-affected years 2020-2021 excluded), the pipeline applies supervised machine learning techniques to predict the annual average number of unemployed persons per district. Data are stored in a normalized relational database (3NF) on the TU Wien DBRepo platform and accessed via its REST API. The best model achieves a test-set RMSE of approximately 1190 and a MAE of approximately 685, demonstrating that overnight stays and population size capture the general unemployment trend well but are insufficient to fully explain higher unemployment concentrations in outer districts.

---

## Table of Contents

1. [Requirements and Installation](#requirements-and-installation)
2. [Step-by-Step Reproduction Instructions](#step-by-step-reproduction-instructions)
3. [Inputs and Outputs](#inputs-and-outputs)
4. [Used Datasets](#used-datasets)
5. [Database Schema and Views (DBRepo)](#database-schema--views-dbrepo)
6. [API Configuration](#api-configuration)
7. [File Organisation](#file-organisation)
8. [Research Object Crate (RO-Crate)](#research-object-crate-ro-crate)
9. [Licences](#licences)
10. [Contributors](#contributors)

---

## Requirements and Installation

### System Requirements

- Python **3.11.9** (other 3.11.x versions may work but are untested)
- Access to the TU Wien DBRepo test instance (internet connection required)
- DBRepo credentials with read access to database `412fb0ce-5299-4d0e-a271-4641b1365b8a`

### Python Dependencies

All dependencies are pinned in `requirements.txt`:

```
pandas==2.3.3
matplotlib==3.10.7
seaborn==0.13.2
scikit-learn==1.7.2
numpy==2.3.4
joblib==1.5.2
pyyaml==6.0.2
dbrepo==1.13.8
python-dotenv==1.2.2
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/nicolasphilipp/unemployment-prediction.git
cd unemployment-prediction

# 2. (Recommended) Create and activate a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Step-by-Step Reproduction Instructions

### Step 0 - Configure Environment Variables

Copy the template and fill in your DBRepo credentials:

```bash
cp config/.env.example config/.env   # or create config/.env manually
```

Edit `config/.env` and set the following four variables (see [API Configuration](#api-configuration) for details).

### Step 1 - Create the Database Schema (one-time, only if you host your own DBRepo instance)

```bash
python src/02_create_database_dbrepo.py
```

This script creates the four relational tables (`district`, `measurement_info`, `unemployment`, `tourism`) in 3NF on the configured DBRepo instance. Skip this step if you are using the existing TU Wien DBRepo database.

### Step 2 - Load Raw Data into DBRepo (one-time)

Open and run all cells of:

```
src/02_load_data_dbrepo.ipynb
```

This notebook reads the two raw CSV files from `data/` and inserts them into the DBRepo tables via the REST API.

### Step 3 - Create SQL Views in DBRepo (one-time)

Open and run all cells of:

```
src/02_load_views_dbrepo.ipynb
```

This creates the `ml_feature_table`, `train_split`, `validation_split`, `test_split`, and the three analytical views inside DBRepo. The view SQL is also found in `docs/views.sql`.

### Step 4 - Semantic and Unit Mapping

These notebooks annotate the database attributes with ontological concepts. They are not required to reproduce the ML results.

```
src/02_semantic_mapping.ipynb
src/02_numeric_unit_mapping_dbrepo.ipynb
```

Outputs from `src/02_semantic_mapping.ipynb` are written to `outputs/semantic_mapping.csv`.

### Step 5 - Run the ML Pipeline

Open and run all cells of the main notebook:

```
src/unemployment_prediction.ipynb
```

The notebook executes the full pipeline in sequence:

1. **Data import** - fetches train, validation, and test splits from DBRepo via `dbrepo_client.py`
2. **Pre-processing** - merges splits, (handles missing values, excludes COVID years (2020-2021) and the aggregate district 90000 - already done in the DBRepo views)
3. **Exploratory Data Analysis (EDA)** - generates time-series and per-district visualisations
4. (**Outlier handling** - formally removes the COVID years identified during EDA - already done in the DBRepo views)
5. **Categorical feature encoding** - one-hot encodes `DISTRICT_CODE` (23 binary columns)
6. (**Train / Validation / Test split** - chronological split (2002-2015 / 2016-2018 / 2019+) - already done in the DBRepo views)
7. **Modelling** - trains Linear Regression and Random Forest with grid-search hyperparameter tuning on validation RMSE
8. **Evaluation** - retrains the best model on combined train+validation data, evaluates on the held-out test set, and saves the model

All outputs (figures, model artefact, processed CSV) are written to the `outputs/` directory automatically.

---

## Inputs and Outputs

### Inputs

| File / Resource                           | Type   | Description                                                                    |
| ----------------------------------------- | ------ | ------------------------------------------------------------------------------ |
| DBRepo REST API - `train_split` view      | API    | Rows for years 2002-2015, ~322 records, used for model training                |
| DBRepo REST API - `validation_split` view | API    | Rows for years 2016-2018, ~69 records, used for hyperparameter tuning          |
| DBRepo REST API - `test_split` view       | API    | Rows for years 2019+ (excl. 2020-2021), ~69 records, used for final evaluation |
| `config/config_general.yaml`              | YAML   | Project paths and version string                                               |
| `config/.env`                             | dotenv | DBRepo credentials (not committed to git)                                      |

**ML Features used in the model:**

| Column          | Description                                             |
| --------------- | ------------------------------------------------------- |
| `TOU_VALUE`     | Total guest overnight stays per district per year       |
| `POP_AVE`       | Average population per district per year                |
| `DISTRICT_CODE` | One-hot encoded district identifier (23 binary columns) |

**Prediction target:** `UEP_VALUE` - annual average number of unemployed persons aged 15-64.

### Outputs

| File                                                             | Type   | Description                                                                                     |
| ---------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------- |
| `outputs/figures/fig_unemployment_tourism_over_time_vX.X.png`    | PNG    | Time-series plot of unemployment and tourism values across all districts                        |
| `outputs/figures/fig_unemployment_tourism_per_district_vX.X.png` | PNG    | Per-district boxplots of unemployment and tourism values                                        |
| `outputs/figures/fig_unemployment_actual_predicted_vX.X.png`     | PNG    | Scatter plot of actual vs predicted unemployment on the test set                                |
| `outputs/figures/data_flow_diagram_horizontal_vX.X.png`          | PNG    | Horizontal data flow diagram of the pipeline                                                    |
| `outputs/figures/data_flow_diagram_vertical_vX.X.png`            | PNG    | Vertical data flow diagram of the pipeline                                                      |
| `outputs/models/model_random_forest_vX.X.pkl`                    | Pickle | Trained Random Forest pipeline (StandardScaler + RandomForestRegressor), serialized with joblib |
| `outputs/semantic_mapping.csv`                                   | CSV    | Semantic annotation of dataset attributes to ontological concepts                               |
| `data/vienna_unemployment_tourism_processed_vX.X.csv`            | CSV    | Merged and cleaned dataset ready for machine learning                                           |

**Model performance (test set, Random Forest):**

| Metric | Value |
| ------ | ----- |
| RMSE   | ~1190 |
| MAE    | ~685  |

---

## Used Datasets

### 1. Unemployed Persons Since 2002 - Districts of Vienna

Stadt Wien - Wirtschaft und Finanzen, _Arbeitslos gemeldete Personen im Alter 15-64 Jahre nach Geschlecht (absolut und pro 1.000 EinwohnerInnen) im Jahresdurchschnitt seit 2002 - Bezirke Wien_, Open Government Data Austria, Dataset ID: `9462d680-ede9-40b9-8102-b9baebaa4fbb`. Available at: https://www.data.gv.at/katalog/dataset/9462d680-ede9-40b9-8102-b9baebaa4fbb (2025). Licence: CC BY 4.0.

**Features:**

| Column              | Description                                                          |
| ------------------- | -------------------------------------------------------------------- |
| `NUTS`              | Statistical region of Austria (always `AT13` for Vienna)             |
| `DISTRICT_CODE`     | Municipality code                                                    |
| `SUB_DISTRICT_CODE` | Census district code (same as municipality code at this granularity) |
| `REF_YEAR`          | Reference year                                                       |
| `REF_DATE`          | Reference date                                                       |
| `SEX`               | 0 = total, 1 = men, 2 = women                                        |
| `UEP_VALUE`         | Average number of unemployed persons (age 15-64)                     |
| `UEP_DENSITY`       | Unemployed persons per 1 000 inhabitants                             |

### 2. Guest Overnight Stays Since 2002 - Districts of Vienna

Stadt Wien - Wirtschaft und Finanzen, _Gästeübernachtungen (absolut und pro 1.000 EinwohnerInnen) seit 2002 - Bezirke Wien_, Open Government Data Austria, Dataset ID: `ae4ebf87-9f46-4f05-9e3d-dbff002b216d`. Available at: https://www.data.gv.at/katalog/datasets/ae4ebf87-9f46-4f05-9e3d-dbff002b216d (2025). Licence: CC BY 4.0.

**Features:**

| Column              | Description                                              |
| ------------------- | -------------------------------------------------------- |
| `NUTS`              | Statistical region of Austria (always `AT13` for Vienna) |
| `DISTRICT_CODE`     | Municipality code                                        |
| `SUB_DISTRICT_CODE` | Census district code                                     |
| `REF_YEAR`          | Reference year                                           |
| `REF_DATE`          | Reference date                                           |
| `TOU_VALUE`         | Total guest overnight stays                              |
| `TOU_DENSITY`       | Overnight stays per 1 000 inhabitants                    |
| `POP_AVE`           | Average population                                       |

---

## Database Schema & Views (DBRepo)

The experiment data is stored in a relational database (3NF) on the TU Wien DBRepo test instance. SQL views de-normalize the schema into query-ready formats for the ML pipeline.

### Database Access

- **DBRepo Instance**: https://test.dbrepo.tuwien.ac.at
- **Database ID**: `412fb0ce-5299-4d0e-a271-4641b1365b8a`
- **Persistent Identifier**: https://doi.org/10.82556/n73d-ks38

### Schema Overview (3NF)

| Table              | Description                                     | Foreign Key                                            |
| ------------------ | ----------------------------------------------- | ------------------------------------------------------ |
| `district`         | Vienna district identifiers and NUTS codes      | `district_id` (PK)                                     |
| `measurement_info` | Temporal and district metadata for measurements | `district_id` -> `district`, `measurement_id` (UNIQUE) |
| `unemployment`     | Unemployment statistics by gender               | `measurement_id` -> `measurement_info`                 |
| `tourism`          | Tourism overnight stay statistics               | `measurement_id` -> `measurement_info`                 |

### SQL Views for the ML Pipeline

The following views de-normalize the schema to support the machine learning workflow. All views are defined in [`docs/views.sql`](docs/views.sql) and implemented in the DBRepo instance.

#### Base Feature View

| View Name          | Purpose                                                                                                                                                   | Key Columns                                                                         |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `ml_feature_table` | Main denormalized feature table joining all sources. Filters: gender = `TOTAL`, excludes district `90000` (Vienna total), excludes COVID years 2020-2021. | `district_code`, `ref_year`, `uep_value`, `uep_density`, `tou_value`, `tou_density` |

#### Data Split Views (Chronological)

| View Name          | Purpose                                   | Time Range | Expected Rows |
| ------------------ | ----------------------------------------- | ---------- | ------------- |
| `train_split`      | Training data for model fitting           | 2002-2015  | ~322          |
| `validation_split` | Validation data for hyperparameter tuning | 2016-2018  | ~69           |
| `test_split`       | Test data for final evaluation            | 2019+      | ~69           |

#### Analytical Views

| View Name                       | Purpose                                                                                                               |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `inner_city_districts`          | Feature table restricted to the nine inner-city districts (90100-90900) with disproportionately high tourism activity |
| `outer_city_districts`          | Feature table restricted to the fourteen outer residential districts (91000-92300) with lower tourism density         |
| `gender_disaggregated_features` | Gender-specific data for models using sex as a predictor (Male/Female only, excludes Both)                            |

**Important notes:**

- The `unemployment` table uses enum values `'Both'`, `'Male'`, `'Female'` for gender.
- Years 2020 and 2021 are excluded from all views as pandemic-driven outliers.

Live views: https://test.dbrepo.tuwien.ac.at/database/412fb0ce-5299-4d0e-a271-4641b1365b8a/view

---

## API Configuration

The experiment loads data exclusively from the DBRepo REST API. Configuration is managed via environment variables in `config/.env`.

| Variable             | Description                                                   |
| -------------------- | ------------------------------------------------------------- |
| `DBREPO_BASE_URL`    | DBRepo instance URL (e.g. `https://test.dbrepo.tuwien.ac.at`) |
| `DBREPO_DATABASE_ID` | Database UUID (`412fb0ce-5299-4d0e-a271-4641b1365b8a`)        |
| `DBREPO_USERNAME`    | Authentication username                                       |
| `DBREPO_PASSWORD`    | Authentication password                                       |

### Usage

```python
from dbrepo_client import create_client

client = create_client()
df_train = client.get_train_data()       # 322 rows (2002-2015)
df_val   = client.get_validation_data()  #  69 rows (2016-2018)
df_test  = client.get_test_data()        #  69 rows (2019+)
```

---

## File Organisation

This project follows a consistent file naming convention to improve clarity, reproducibility, and ease of collaboration. The structure is organised into dedicated directories based on file purpose.

```
config/
data/
docs/
  └── validation/
outputs/
  ├── figures/
  ├── metadata/
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

### Naming Conventions

- Lowercase letters and underscores only.
- Avoid spaces and special characters.
- Datasets and model artefacts are versioned with `_v1.0`, `_v2.0`, etc.
- Source scripts use numeric prefixes (`01_`, `02_`, ...) to indicate workflow order.
- Keep names descriptive but concise.

---

## Research Object Crate (RO-Crate)

This repository includes a valid [RO-Crate](https://www.researchobject.org/ro-crate/) metadata file describing the entire experiment package - datasets, model, code, and authors.

- **RO-Crate Metadata:** [`ro-crate-metadata.json`](./ro-crate-metadata.json)
- **Validation Report:** [`docs/validation/ro-crate-validation.txt`](./docs/validation/ro-crate-validation.txt)

---

## Licences

This project applies three separate licences reflecting the different nature of its components.

### Code Licence - MIT License

The source code in this repository (`src/`) is released under the **MIT License**. The MIT License was selected because it is a permissive open-source licence that allows reuse, modification, distribution, and academic extension with minimal restrictions. This makes it fully compatible with the open reuse conditions of the source datasets while supporting transparency and reproducibility.

```
MIT License

Copyright (c) 2026 Florian Angerer, Swetha Maria Siby, Nicolas Philipp, Midhun Suresh Nair

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Full SPDX identifier: [`MIT`](https://spdx.org/licenses/MIT)

---

### Data Licence - Creative Commons Attribution 4.0 International (CC BY 4.0)

The input datasets (`data/`) originate from the Austrian Open Government Data portal and are published under the **Creative Commons Attribution 4.0 International** licence. The processed derivative dataset (`data/vienna_unemployment_tourism_processed_vX.X.csv`) is released under the same licence. These licences allow processing, transformation, and derivative analysis provided that proper attribution to the original publisher is maintained. All original dataset references and source URLs are preserved throughout the project documentation.

> You are free to share and adapt the data for any purpose, provided you give appropriate credit, provide a link to the licence, and indicate if changes were made.

Full licence text: https://creativecommons.org/licenses/by/4.0/  
SPDX identifier: [`CC-BY-4.0`](https://spdx.org/licenses/CC-BY-4.0)

---

### Produced / Output Data Licence

All generated project artefacts, including:

- processed datasets
- trained machine learning models
- generated figures
- semantic metadata files
- documentation outputs

are licensed under **CC BY 4.0**.

This licence permits reuse, redistribution, and adaptation provided appropriate attribution is given to the project authors.

---

## Contributors

All contributors are affiliated with [TU Wien](https://www.tuwien.ac.at) ([ROR: 04d836q62](https://ror.org/04d836q62)).

| Name               | ORCID                                                        |
| ------------------ | ------------------------------------------------------------ |
| Florian Angerer    | [0009-0001-5857-4758](https://orcid.org/0009-0001-5857-4758) |
| Swetha Maria Siby  | [0009-0001-9927-9405](https://orcid.org/0009-0001-9927-9405) |
| Nicolas Philipp    | [0009-0004-9308-5919](https://orcid.org/0009-0004-9308-5919) |
| Midhun Suresh Nair | [0009-0001-1784-2808](https://orcid.org/0009-0001-1784-2808) |
