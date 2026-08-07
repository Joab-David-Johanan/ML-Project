# Munich Bicycle Demand and Parking Pressure

Data-driven decision support for forecasting bicycle demand pressure near Munich counting stations and parking infrastructure.

## Table of Contents

1. [Project Summary](#project-summary)
2. [Business Objective](#business-objective)
3. [ML Business Logic](#ml-business-logic)
4. [Current Datasets](#current-datasets)
5. [Station Caveats](#station-caveats)
6. [Repository Layout](#repository-layout)
7. [Status](#status)

## Project Summary

This project combines time-series bicycle counts, parking capacity, and cycling network context to estimate when and where parking pressure is likely to increase in Munich.

## Business Objective

Forecast short-term cycling demand and translate it into location-level parking pressure signals so city operators can prioritize interventions, capacity planning, and operational reviews across Bike+Ride and decentralized parking.

## ML Business Logic

1. Forecast demand at counting stations using 15-minute and daily historical patterns.
2. Link station demand to nearby parking assets using spatial proximity and path context.
3. Estimate effective local capacity from active parking records and parking type metadata.
4. Produce a pressure risk score per location and time window for operational prioritization.
5. Segment outputs by Bike+Ride vs decentralized parking for targeted actions.

## Current Datasets

Raw data is organized by domain under `data/raw`.

### Cycle counts

Location: `data/raw/cycle_counts`

| File | Format | Purpose |
|---|---|---|
| `2017_2024/counting_stations.csv` | CSV | Counting station metadata |
| `2017_2024/cycle_count_15min.csv` | CSV | Historical 15-minute counts (2017-2024) |
| `2017_2024/cycle_count_day.csv` | CSV | Historical daily counts with weather context (2017-2024) |
| `2025/rad_YYYY_MM_15min.csv` | CSV | Monthly 15-minute counts for 2025 |
| `2025/rad_YYYY_MM_tage.csv` | CSV | Monthly daily/weather counts for 2025 |
| `2026/rad_YYYY_MM_15min.csv` | CSV | Monthly 15-minute counts for 2026 |
| `2026/rad_YYYY_MM_tage.csv` | CSV | Monthly daily/weather counts for 2026 |

### Cycle parking

Location: `data/raw/cycle_parking`

| File | Format | Purpose |
|---|---|---|
| `cycle_parking_public.csv` | CSV | Public parking snapshot (legacy/reference) |
| `cycle_parking_total.csv` | CSV | Primary parking inventory (Bike+Ride + decentralized + status + capacity) |
| `cycle_parking_total.json` | JSON | Geospatial JSON representation of total parking inventory |

### Cycle paths

Location: `data/raw/cycle_paths`

| File | Format | Purpose |
|---|---|---|
| `cycle_paths.csv` | CSV | Urban cycle path attributes for feature engineering |
| `cycle_paths_rural.json` | JSON | Rural cycle path context layer |
| `cycle_paths_rural_WFS.zip` | ZIP | Source WFS archive for rural path geodata |

## Station Caveats

Data quality note: station-specific caveats are treated as modeling constraints, and outputs should be interpreted as demand-pressure estimates rather than exact occupancy truth.

1. Margaretenstr. (Harras): sensor malfunction after construction work.
2. Arnulfstr. 9-11 (south side): this station is not on a two-way cycle path; direction 2 captures counterflow bicycles.

Modeling implications:

1. Use `gesamt` for cross-station comparability.
2. Treat Margareten post-failure periods as unreliable or excluded in longitudinal modeling.
3. Use station-specific flags for direction semantics where direction-level analysis is required.

## Repository Layout

- `conf`: configuration groups (data, model, trainer, experiment)
- `src/forecast_app`: application code for data, features, models, dashboard, utils
- `pipelines`: runnable pipeline entry points
- `data/raw/cycle_counts`, `data/raw/cycle_parking`, `data/raw/cycle_paths`: domain-grouped raw inputs
- `data/interim`, `data/processed`: transformed and model-ready layers
- `tests`: validation and smoke tests
- `artifacts`: model, metrics, and reporting outputs

## Status

Scaffold and domain-grouped datasets are in place. Next milestone is preprocessing, station-parking mapping, and baseline forecasting with pressure scoring.
