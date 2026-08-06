# UV Setup Steps

## Table of Contents

1. [Step 1: Initialize project](#step-1-initialize-project)
2. [Step 2: Add NumPy](#step-2-add-numpy)
3. [Step 3: Change Python version after uv init](#step-3-change-python-version-after-uv-init)
4. [Step 4: Project repository structure](#step-4-project-repository-structure)
5. [Step 5: Editable install for local package imports](#step-5-editable-install-for-local-package-imports)

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
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
├── uv.lock
├── artifacts/
│   ├── metrics/
│   ├── models/
│   └── reports/
├── conf/
│   ├── config.yaml
│   ├── data/
│   ├── experiment/
│   ├── model/
│   └── trainer/
├── data/
│   ├── external/
│   ├── interim/
│   ├── processed/
│   └── raw/
├── notebooks/
├── notes/
├── pipelines/
├── scripts/
├── src/
│   └── forecast_app/
└── tests/
```

Brief explanation of each top-level folder:

1. conf: Hydra and OmegaConf configuration groups for data, model, trainer, and experiments.
2. data/raw: immutable source files.
3. data/interim: temporary transformed files.
4. data/processed: model-ready datasets.
5. src/forecast_app: core application and ML pipeline code.
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