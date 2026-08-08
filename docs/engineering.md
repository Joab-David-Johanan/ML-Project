# Engineering Notes: Munich Cycle Demand Project

## Table of Contents

1. [Project Intent](#project-intent)
2. [Problem Framing Evolution](#problem-framing-evolution)
3. [Major Decisions Taken](#major-decisions-taken)
4. [Data Collection Workflow](#data-collection-workflow)
5. [Data Ingestion Workflow](#data-ingestion-workflow)
6. [Current Data Architecture](#current-data-architecture)
7. [Skills to Focus On](#skills-to-focus-on)
8. [Configuration and Validation Contracts](#configuration-and-validation-contracts)
9. [Cited Sources](#cited-sources)
10. [Additional Work Completed](#additional-work-completed)
11. [Next Engineering Milestones](#next-engineering-milestones)

## Project Intent

Build a decision-support demand forecasting app for Munich bicycle traffic and parking pressure.

Context and motivation:

- Munich has a strong and growing cycling mobility focus.
- The city provides both Bike+Ride and decentralized bicycle parking infrastructure.
- Counting stations, parking capacity, and cycle path data are available and can be combined for forecasting and planning.

Evidence note:

- We treat "cycling growth" as policy and infrastructure context backed by official city sources, not as an absolute claim that bicycle traffic is always higher than car traffic citywide.

Initial objective:

- Forecast cycle demand by time and location.
- Translate demand into parking pressure risk signals for operational planning.

[Back to TOC](#table-of-contents)

## Problem Framing Evolution

1. First framing:

- Predict demand from cycle count time series.

2. Improved framing:

- Predict demand pressure near parking infrastructure by combining:
  - count stations
  - parking capacity
  - path accessibility context

3. Final practical framing:

- Produce planning-grade pressure estimates and prioritization signals, not direct real-time occupancy truth.

Why this framing is solid:

- It matches available data.
- It avoids over-claiming unsupported outcomes.
- It is useful for city operations and portfolio storytelling.

[Back to TOC](#table-of-contents)

## Major Decisions Taken

1. Use Munich-specific data instead of generic benchmark datasets.
2. Keep the pipeline reproducible with a clear raw -> processed flow.
3. Keep two canonical count outputs at the interim layer until final curation is implemented:
   - cycle_count_15
   - cycle_count_day
4. Use Parquet only for interim and processed layers to avoid duplicate storage and schema drift between file formats.
5. Keep counting station metadata alongside interim count outputs for stable joins.
6. Use `cycle_parking_total` as primary parking inventory source.
7. Document station caveats explicitly:
   - Margaretenstr. (Harras) sensor malfunction after construction.
   - Arnulfstr. direction semantics are station-specific.
8. Use Ruff for lint/format consistency.
9. Keep command and engineering docs in `docs/` for repeatable workflow.

[Back to TOC](#table-of-contents)

## Data Collection Workflow

Goal:

- Gather all required sources and preserve them in immutable raw form.

What was collected:

1. Cycle counts
   - 2017-2024 combined 15-minute and daily files
   - 2025 monthly 15-minute and daily files
   - 2026 monthly 15-minute and daily files
2. Counting station metadata
3. Parking datasets
   - public snapshot
   - total inventory with Bike+Ride and decentralized coverage
4. Cycle path datasets
   - urban path attributes
   - rural path context

Consistency checks to perform during collection:

1. Header/schema consistency across months and years
2. Date format consistency (`yyyy.mm.dd`)
3. Time format consistency (`hh:mm`)
4. Station name consistency (`zaehlstelle`)
5. File naming conventions by year/month/suffix
6. Source freshness and update timestamps

Key engineering principle:

- Never edit raw files in place. Keep source data immutable and normalize in processing code.

[Back to TOC](#table-of-contents)

## Data Ingestion Workflow

Goal:

- Combine and normalize raw data into reproducible interim datasets before final curated processing.

Current ingestion design:

1. Read historical combined files (2017-2024).
2. Read each monthly file for 2025 and 2026.
3. Normalize schema:
   - trim column names
   - normalize date/time text
   - cast numeric columns safely
4. Concatenate all files by granularity.
5. Drop exact duplicates.
6. Sort deterministically.
7. Write outputs to `data/interim/cycle_counts` as Parquet only.
8. Export counting stations metadata into interim for join stability.

Key points that matter here:

1. Ingestion is file-driven, not assumption-driven.
2. Missing or malformed files should fail loudly or be logged clearly.
3. Interim layer should be deterministic and reproducible.
4. Keep one canonical output per granularity.

Expected outputs:

1. `cycle_count_15.parquet`
2. `cycle_count_day.parquet`
3. `counting_stations.parquet`

[Back to TOC](#table-of-contents)

## Current Data Architecture

```text
data/raw/
  cycle_counts/
    2017_2024/
    2025/
    2026/
  cycle_parking/
  cycle_paths/

data/interim/
  cycle_counts/
      cycle_count_15.parquet
      cycle_count_day.parquet
      counting_stations.parquet

data/processed/
   cycle_counts/
      <empty until final curated datasets are built>
```

Architecture rationale:

1. Raw is source-of-truth immutable storage.
2. Interim stores merged normalized outputs; processed is reserved for final curated datasets.
3. Clear separation simplifies debugging and reproducibility.

[Back to TOC](#table-of-contents)

## Configuration and Validation Contracts

Purpose:

- Ensure every experiment uses explicit defaults and every processed dataset passes a consistent validation interface.

Implemented configuration contracts:

1. `conf/config.yaml`
   - defaults for `data`, `model`, and `trainer`
   - explicit `_self_` usage for deterministic config composition
   - task contract for target, horizon, split strategy, and metrics
2. `conf/data/local.yaml` and `conf/data/prod.yaml`
   - explicit Parquet input paths for counts, parking, and paths

Implemented validation contracts:

1. `src/forecast_app/data/validate.py`
   - hard data integrity errors raise exceptions
   - warning-level findings are returned as `ValidationIssue` list
   - all `_validate_*` functions now use the same contract style
2. `pipelines/run_validate.py`
   - dedicated entrypoint to run validation like other pipelines
3. `src/forecast_app/data/schemas.py`
   - dataframe contracts for required columns, expected types, and numeric bounds
   - separate classification for missing values, invalid types, and invalid values

Why this matters:

1. Config composition and task definitions are deterministic.
2. Validation outcomes are unambiguous: failed, warnings, or clean success.
3. Adding new domains stays consistent with one validator interface.

[Back to TOC](#table-of-contents)

## Skills to Focus On

### 1) Data Collection and Governance

Focus skills:

1. Source discovery and selection
2. Data quality profiling
3. Schema versioning awareness
4. Documentation of caveats and assumptions

What good looks like:

- You can justify every dataset and its role.
- You can explain trust boundaries of each source.

### 2) Data Ingestion Engineering

Focus skills:

1. Building idempotent ingestion scripts
2. Schema normalization across time
3. Robust typing and null handling
4. Deterministic output generation
5. Structured logging and basic validation checks

What good looks like:

- Re-running ingestion yields stable outputs.
- New monthly files are absorbed with minimal code changes.

### 3) Time-Series Data Engineering

Focus skills:

1. Temporal consistency checks
2. Frequency handling (15-min vs daily)
3. Station-level continuity analysis
4. Caveat-aware handling of sensor anomalies

### 4) Geospatial Data Integration

Focus skills:

1. Coordinate normalization
2. Spatial joins and proximity mapping
3. Merging station, parking, and path context

### 5) Software and Team Workflow

Focus skills:

1. Clean project structure
2. Commit discipline
3. Linting/formatting hygiene
4. Reproducible commands and notes

### 6) Debugging and Data Reliability

Focus skills:

1. Detecting and fixing file/content corruption quickly
2. Diagnosing import/runtime issues across notebooks and scripts
3. Designing caveat-aware data handling rules
4. Separating hard facts from assumptions in project claims

[Back to TOC](#table-of-contents)

## Additional Work Completed

Important completed work that should be considered part of the engineering journey:

1. Repaired scaffold files that were generated with literal backtick-n artifacts.
2. Normalized project packaging and import paths for stable notebook/script usage.
3. Profiled and validated raw datasets before model framing decisions.
4. Verified station continuity across years and documented station caveats.
5. Confirmed JSON/GeoJSON validity before using geospatial context layers.
6. Added source citations and tightened wording to avoid unsupported absolute claims.
7. Added explicit Hydra task defaults and data-profile input contracts.
8. Standardized validation function behavior and added a dedicated `run_validate` pipeline entrypoint.
9. Migrated count outputs to interim-only Parquet storage and emptied the processed layer.
10. Refactored schema-contract tests to idiomatic `pytest` patterns with fixtures and `pytest.raises`.

[Back to TOC](#table-of-contents)

## Cited Sources

1. Munich city bicycle parking information (official):
   - https://muenchenunterwegs.de/information/fahrradparken
   - Used for: Bike+Ride and decentralized parking context, ongoing expansion, and operational notes (including removal of abandoned bikes).

2. Munich Open Data Portal (official city portal):
   - https://opendata.muenchen.de/
   - Used for: source governance context and dataset provenance.

3. Munich Radlstadtplan rural paths dataset page:
   - https://opendata.muenchen.de/dataset/rad_rsp_radwege_forstfeld_line
   - Used for: cycle path rural-context layer, license/provenance notes, and spatial-accuracy disclaimer.

4. Munich parking map/service links (official):
   - https://go.muenchen.de/fahrradparken
   - https://muenchenunterwegs.de/angebote/hilfestellung-neue-fahrradabstellplaetze-beantragen
   - Used for: practical operations context and public process for requesting new parking spots.

Access date for all links above: 2026-08-07.

[Back to TOC](#table-of-contents)

## Next Engineering Milestones

1. Add ingestion validation reports (row counts, unique stations, date ranges).
2. Build feature engineering for demand-pressure modeling.
3. Add tests for ingest edge cases and schema drift.
4. Create baseline forecast model and evaluation pipeline.
5. Add dashboard layer for pressure hotspots and trends.

[Back to TOC](#table-of-contents)
