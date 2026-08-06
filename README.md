# Munich Bicycle Demand and Parking Pressure

Data-driven decision support for forecasting bicycle demand pressure near Munich counting stations and parking infrastructure.

## Table of Contents

1. [Project Summary](#project-summary)
2. [Business Objective](#business-objective)
3. [ML Business Logic](#ml-business-logic)
4. [Current Datasets](#current-datasets)
5. [Repository Layout](#repository-layout)
6. [Status](#status)

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

All files currently in `data/raw`:

| File | Format | Purpose |
|---|---|---|
| `counting_stations.csv` | CSV | Counting station metadata and location reference |
| `cycle_count_15min.csv` | CSV | High-frequency demand signal (15-minute bicycle counts) |
| `cycle_count_day.csv` | CSV | Daily demand aggregate and weather context |
| `cycle_parking.csv` | CSV | Legacy parking snapshot with capacity and transit context |
| `cycle_parking_2.csv` | CSV | Primary parking inventory (Bike+Ride + decentralized + status + capacity) |
| `cycle_parking_2.json` | JSON | Parking dataset in geospatial JSON form |
| `cycle_paths.csv` | CSV | Cycling path attributes for spatial feature engineering |
| `cycle_paths_rural.json` | JSON | Rural cycling path context layer |
| `cycle_paths_rural_WFS.zip` | ZIP (WFS export) | Source package for rural path geodata |

## Repository Layout

- `conf`: configuration groups (data, model, trainer, experiment)
- `src/forecast_app`: application code for data, features, models, dashboard, utils
- `pipelines`: runnable pipeline entry points
- `data/raw`, `data/interim`, `data/processed`: data lifecycle layers
- `tests`: validation and smoke tests
- `artifacts`: model, metrics, and reporting outputs

## Status

Scaffold and data inventory are in place. Next milestone is preprocessing, geospatial mapping, and baseline forecasting with pressure scoring.
