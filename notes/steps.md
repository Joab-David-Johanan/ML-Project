# UV Setup Steps

## Table of Contents

1. [Step 1: Initialize project](#step-1-initialize-project)
2. [Step 2: Add NumPy](#step-2-add-numpy)
3. [Step 3: Change Python version after uv init](#step-3-change-python-version-after-uv-init)
4. [Step 4: Project repository structure](#step-4-project-repository-structure)
5. [Step 5: Editable install for local package imports](#step-5-editable-install-for-local-package-imports)
6. [Step 6: Organize raw datasets by domain](#step-6-organize-raw-datasets-by-domain)
7. [Step 7: Merge cycle count files into processed outputs](#step-7-merge-cycle-count-files-into-processed-outputs)
8. [Step 8: Enable Parquet export](#step-8-enable-parquet-export)
9. [Step 9: Export counting station metadata](#step-9-export-counting-station-metadata)
10. [Step 10: Ruff lint and formatting workflow](#step-10-ruff-lint-and-formatting-workflow)
11. [Step 11: Commit workflow used](#step-11-commit-workflow-used)
12. [Step 12: Libraries added and install commands](#step-12-libraries-added-and-install-commands)
13. [Step 13: Command glossary](#step-13-command-glossary)

## Step 1: Initialize project

Command:

```bash
uv init
```

Run in order:

```bash
uv init
```

[Back to TOC](#table-of-contents)

## Step 2: Add NumPy

Command:

```bash
uv add numpy
```

Run in order:

```bash
uv add numpy
```

[Back to TOC](#table-of-contents)

## Step 3: Change Python version after uv init

If `uv init` picked Python 3.12 and you want 3.13, update the project target and pin:

1. Install Python 3.13 for uv:

   ```bash
   uv python install 3.13
   ```
2. Pin the project to 3.13:

   ```bash
   uv python pin 3.13
   ```
3. Ensure `pyproject.toml` matches the target version:

   ```bash
   # in pyproject.toml
   requires-python = ">=3.13"
   ```
4. Re-sync environment and lockfile:

   ```bash
   uv sync
   ```

Run in order:

```bash
uv python install 3.13
uv python pin 3.13
uv sync
```

Also ensure this value in pyproject.toml before syncing:

```bash
# in pyproject.toml
requires-python = ">=3.13"
```

After this, uv will use Python 3.13 for this project.

[Back to TOC](#table-of-contents)

## Step 4: Project repository structure

Purpose:

- Keep data, code, configs, notebooks, and pipelines separated so the project is easier to scale.

Structure:

```text
ML Project/
├── .ruff_cache/
├── artifacts/
│   ├── metrics/
│   ├── models/
│   └── reports/
├── conf/
│   ├── config.yaml
│   ├── data/
│   │   ├── local.yaml
│   │   └── prod.yaml
│   ├── experiment/
│   │   ├── baseline_local.yaml
│   │   └── lgbm_prod.yaml
│   ├── model/
│   │   ├── baseline.yaml
│   │   └── lgbm.yaml
│   └── trainer/
│       ├── fast.yaml
│       └── full.yaml
├── data/
│   ├── external/
│   ├── interim/
│   ├── processed/
│   │   └── cycle_counts/
│   │       ├── counting_stations.csv
│   │       ├── counting_stations.parquet
│   │       ├── cycle_count_15.csv
│   │       ├── cycle_count_15.parquet
│   │       ├── cycle_count_day.csv
│   │       └── cycle_count_day.parquet
│   └── raw/
│       ├── cycle_counts/
│       │   ├── 2017_2024/
│       │   │   ├── counting_stations.csv
│       │   │   ├── cycle_count_15min.csv
│       │   │   └── cycle_count_day.csv
│       │   ├── 2025/
│       │   │   ├── rad_2025_01_15min.csv
│       │   │   ├── rad_2025_01_tage.csv
│       │   │   ├── ...
│       │   │   ├── rad_2025_12_15min.csv
│       │   │   └── rad_2025_12_tage.csv
│       │   └── 2026/
│       │       ├── rad_2026_01_15min.csv
│       │       ├── rad_2026_01_tage.csv
│       │       ├── ...
│       │       ├── rad_2026_07_15min.csv
│       │       └── rad_2026_07_tage.csv
│       ├── cycle_parking/
│       │   ├── cycle_parking_public.csv
│       │   ├── cycle_parking_total.csv
│       │   └── cycle_parking_total.json
│       └── cycle_paths/
│           ├── cycle_paths.csv
│           ├── cycle_paths_rural.json
│           └── cycle_paths_rural_WFS.zip
├── notebooks/
│   ├── 01_eda_br.ipynb
│   └── 02_counting_stations.ipynb
├── notes/
│   ├── decisions.md
│   └── steps.md
├── pipelines/
│   ├── run_forecast.py
│   ├── run_ingest.py
│   └── run_train.py
├── scripts/
│   ├── run_dashboard.ps1
│   └── setup_env.ps1
├── src/
│   ├── forecast_app/
│   │   ├── __init__.py
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── dashboard/
│   │   │   └── app.py
│   │   ├── data/
│   │   │   ├── ingest.py
│   │   │   ├── preprocess.py
│   │   │   └── validate.py
│   │   ├── features/
│   │   │   └── build_features.py
│   │   ├── models/
│   │   │   ├── evaluate.py
│   │   │   ├── predict.py
│   │   │   └── train.py
│   │   └── utils/
│   │       ├── logging.py
│   │       └── paths.py
│   └── ml_project.egg-info/
├── tests/
│   ├── test_data_validation.py
│   ├── test_features.py
│   └── test_train_smoke.py
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

Brief explanation of each top-level folder:

1. conf: Hydra and OmegaConf configuration groups for data, model, trainer, and experiments.
2. data/raw: immutable source files organized by counts, parking, and paths.
3. data/interim: temporary transformed files.
4. data/processed: model-ready consolidated outputs (CSV and Parquet).
5. src/forecast_app: core package where ingest, feature engineering, models, and utilities live.
6. pipelines: runnable entrypoints for ingest, train, and forecast jobs.
7. tests: smoke and unit tests.
8. artifacts: generated outputs such as models, metrics, and reports.
9. notebooks: exploration and analysis only.
10. notes: process logs and project decisions.

[Back to TOC](#table-of-contents)

## Step 5: Editable install for local package imports

Purpose:

- Make imports like from forecast_app... work from notebooks, tests, and scripts without path hacks.

Why this helps:

1. Code edits are available immediately without reinstalling.
2. Package imports are consistent across the repository.
3. It matches real production packaging workflows.

Run in order:

```bash
uv sync
uv pip install -e .
```

Verify quickly:

```bash
uv run python -c "from forecast_app.config.settings import settings; print(settings.app_env)"
```

If import fails in notebook:

1. Ensure the notebook kernel uses this project virtual environment.
2. Restart the kernel after editable install.

[Back to TOC](#table-of-contents)

## Step 6: Organize raw datasets by domain

Purpose:

- Keep raw files grouped by business domain for easier ingestion and maintenance.

Resulting structure:

```text
data/raw/
├── cycle_counts/
│   ├── 2017_2024/
│   ├── 2025/
│   └── 2026/
├── cycle_parking/
└── cycle_paths/
```

Command pattern used:

```bash
git add -A data/raw
```

Brief explanation:

1. We moved and renamed files into clear domain folders.
2. This simplifies downstream code because each data source has one home.

[Back to TOC](#table-of-contents)

## Step 7: Merge cycle count files into processed outputs

Purpose:

- Convert many yearly/monthly raw count files into two clean analysis-ready datasets.

Run command:

```bash
uv run python pipelines/run_ingest.py
```

What this does:

1. Merges all 15-minute files from 2017 to 2026 into one file.
2. Merges all daily files from 2017 to 2026 into one file.
3. Normalizes dates/times and numeric columns.
4. Removes duplicate rows and sorts output.

Output files:

1. `data/processed/cycle_counts/cycle_count_15.csv`
2. `data/processed/cycle_counts/cycle_count_day.csv`
3. `data/processed/cycle_counts/cycle_count_15.parquet`
4. `data/processed/cycle_counts/cycle_count_day.parquet`

[Back to TOC](#table-of-contents)

## Step 8: Enable Parquet export

Purpose:

- Use Parquet for faster and more storage-efficient analytics workloads.

Run command:

```bash
uv add pyarrow
```

Brief explanation:

1. Pandas requires a parquet engine.
2. `pyarrow` enables `DataFrame.to_parquet(...)` in the ingest pipeline.

[Back to TOC](#table-of-contents)

## Step 9: Export counting station metadata

Purpose:

- Keep station location metadata in processed so model and joins always use one canonical reference.

Run command:

```bash
uv run python pipelines/run_ingest.py
```

Output files:

1. `data/processed/cycle_counts/counting_stations.csv`
2. `data/processed/cycle_counts/counting_stations.parquet`

Brief explanation:

1. Even though one station is missing in later years, metadata is still needed for geospatial joins.

[Back to TOC](#table-of-contents)

## Step 10: Ruff lint and formatting workflow

Purpose:

- Keep code quality high and formatting consistent before commits.

Run in order:

```bash
uv run ruff check . --fix
uv run ruff format .
```

Brief explanation:

1. `check --fix` applies auto-fixable lint rules.
2. `format` applies deterministic code formatting.

[Back to TOC](#table-of-contents)

## Step 11: Commit workflow used

Purpose:

- Keep history reviewable with focused commits per concern.

Typical commands used:

```bash
git status --short
git add <files>
git commit -m "<clear message>"
git log --oneline -n 5
```

Brief explanation:

1. Separate commits were created for docs updates, data refresh/reorganization, and pipeline updates.
2. This keeps review and rollback clean.

[Back to TOC](#table-of-contents)

## Step 12: Libraries added and install commands

Purpose:

- Keep a clear record of package additions and the exact commands used.

Commands used (confirmed by current project state):

1. NumPy

   ```bash
   uv add numpy
   ```

   Brief explanation:

   - Adds NumPy as a project dependency for numerical operations.

2. PyArrow

   ```bash
   uv add pyarrow
   ```

   Brief explanation:

   - Adds the parquet engine used by pandas for `.to_parquet(...)` output.

3. Editable local package install (forecast_app import support)

   ```bash
   uv pip install -e .
   ```

   Brief explanation:

   - Installs the local project package in editable mode for notebooks, scripts, and tests.

4. Ruff (if not already present)

   ```bash
   uv add --dev ruff
   ```

   Brief explanation:

   - Adds Ruff for linting and formatting as a development dependency.

[Back to TOC](#table-of-contents)

## Step 13: Command glossary

Purpose:

- Explain exactly what each frequently used command does in this project.

### UV commands

1. `uv init`

   - Creates a new Python project scaffold.
   - Initializes `pyproject.toml`.

2. `uv add <package>` (example: `uv add numpy`)

   - Adds the dependency to `pyproject.toml`.
   - Updates `uv.lock`.
   - Installs the package into the project virtual environment.
   - If `.venv` does not exist, uv creates and manages it automatically.
   - Because `uv add` already updates lockfile and environment, you do not need to run `uv sync` immediately after `uv add`.

3. `uv add --dev <package>` (example: `uv add --dev ruff`)

   - Adds a package to the dev dependency group.
   - Updates both `pyproject.toml` and `uv.lock`.
   - Installs into `.venv`.

4. `uv sync`

   - Synchronizes `.venv` to match `pyproject.toml` and `uv.lock` exactly.
   - Use it when pulling changes from git or after manual dependency edits.

5. `uv pip install -e .`

   - Installs the local project package in editable mode.
   - Imports like `from forecast_app...` work from notebooks, scripts, and tests.

6. `uv run python pipelines/run_ingest.py`

   - Runs the ingest pipeline in the project environment.
   - Produces merged processed outputs from raw cycle count files.

7. `uv run ruff check . --fix`

   - Runs lint checks and auto-fixes issues Ruff can fix safely.

8. `uv run ruff format .`

   - Applies consistent code formatting across the repository.

### Git commands

1. `git status --short`

   - Shows concise file status codes (`M`, `A`, `D`, `??`) instead of verbose output.
   - Useful for quick staging decisions.

2. `git add <files>`

   - Stages selected files for the next commit.

3. `git add -A`

   - Stages all tracked/untracked/deleted changes.

4. `git commit -m "message"`

   - Creates a commit from staged changes with a commit message.

5. `git log --oneline -n 5`

   - Shows the latest 5 commits in compact one-line format.

[Back to TOC](#table-of-contents)