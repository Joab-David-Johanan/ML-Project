from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from forecast_app.data.schemas import (
    CountingStationsContract,
    CycleCount15Contract,
    CycleCountDayContract,
    validate_dataframe_contract,
)
from forecast_app.utils.paths import PROJECT_ROOT


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    message: str


def _parse_simple_yaml(file_path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Keep only top-level scalar keys from this minimal parser.
        if key and value and not key.startswith("-"):
            data[key] = value
    return data


def _resolve_processed_path(profile: str = "local") -> Path:
    conf_path = PROJECT_ROOT / "conf" / "data" / f"{profile}.yaml"
    if not conf_path.exists():
        raise FileNotFoundError(f"Missing data profile config: {conf_path}")

    config = _parse_simple_yaml(conf_path)
    processed_path = config.get("processed_path")
    if not processed_path:
        raise ValueError(f"Missing 'processed_path' in config: {conf_path}")

    path = Path(processed_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _assert_required_columns(
    df: pd.DataFrame, required: set[str], dataset_name: str
) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{dataset_name}: missing required columns: {sorted(missing)}")


def _assert_no_nulls(df: pd.DataFrame, cols: list[str], dataset_name: str) -> None:
    null_counts = df[cols].isnull().sum()
    bad = {col: int(count) for col, count in null_counts.items() if int(count) > 0}
    if bad:
        raise ValueError(f"{dataset_name}: null values in key columns: {bad}")


def _assert_no_duplicates(
    df: pd.DataFrame, subset: list[str], dataset_name: str
) -> None:
    dup_count = int(df.duplicated(subset=subset).sum())
    if dup_count > 0:
        raise ValueError(
            f"{dataset_name}: found {dup_count} duplicate rows for key {subset}"
        )


def _assert_non_negative(df: pd.DataFrame, cols: list[str], dataset_name: str) -> None:
    for col in cols:
        values = pd.to_numeric(df[col], errors="coerce")
        if values.isnull().any():
            raise ValueError(
                f"{dataset_name}: non-numeric values found in numeric column '{col}'"
            )
        negatives = int((values < 0).sum())
        if negatives > 0:
            raise ValueError(
                f"{dataset_name}: found {negatives} negative values in '{col}'"
            )


def _assert_daily_continuity(day_df: pd.DataFrame) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    work = day_df.copy()
    work["date"] = pd.to_datetime(work["datum"], format="%Y.%m.%d", errors="coerce")
    if work["date"].isnull().any():
        bad = int(work["date"].isnull().sum())
        raise ValueError(
            f"cycle_count_day.parquet: failed to parse {bad} rows in 'datum' as %Y.%m.%d"
        )

    for station, grp in work.groupby("zaehlstelle"):
        sorted_dates = grp["date"].drop_duplicates().sort_values()
        if sorted_dates.empty:
            continue
        max_gap = int(sorted_dates.diff().dropna().dt.days.max() or 0)
        if max_gap > 1:
            issues.append(
                ValidationIssue(
                    level="warning",
                    message=f"cycle_count_day.parquet: station '{station}' has date gaps up to {max_gap} day(s)",
                )
            )
    return issues


def _validate_cycle_counts(base: Path) -> list[ValidationIssue]:
    day_path = base / "cycle_counts" / "cycle_count_day.parquet"
    qh_path = base / "cycle_counts" / "cycle_count_15.parquet"
    stations_path = base / "cycle_counts" / "counting_stations.parquet"

    for path in [day_path, qh_path, stations_path]:
        if not path.exists():
            raise FileNotFoundError(
                f"Missing required processed cycle counts file: {path}"
            )

    day_df = pd.read_parquet(day_path)
    qh_df = pd.read_parquet(qh_path)
    stations_df = pd.read_parquet(stations_path)

    validate_dataframe_contract(
        day_df, CycleCountDayContract, "cycle_count_day.parquet"
    )
    validate_dataframe_contract(qh_df, CycleCount15Contract, "cycle_count_15.parquet")
    validate_dataframe_contract(
        stations_df, CountingStationsContract, "counting_stations.parquet"
    )

    _assert_no_nulls(
        day_df, ["datum", "zaehlstelle", "gesamt"], "cycle_count_day.parquet"
    )
    _assert_no_nulls(
        qh_df,
        ["datum", "uhrzeit_start", "zaehlstelle", "gesamt"],
        "cycle_count_15.parquet",
    )
    _assert_no_nulls(
        stations_df,
        ["zaehlstelle", "latitude", "longitude"],
        "counting_stations.parquet",
    )

    _assert_no_duplicates(day_df, ["datum", "zaehlstelle"], "cycle_count_day.parquet")
    _assert_no_duplicates(
        qh_df,
        ["datum", "uhrzeit_start", "zaehlstelle"],
        "cycle_count_15.parquet",
    )
    _assert_no_duplicates(stations_df, ["zaehlstelle"], "counting_stations.parquet")

    _assert_non_negative(
        day_df, ["richtung_1", "richtung_2", "gesamt"], "cycle_count_day.parquet"
    )
    _assert_non_negative(
        qh_df,
        ["richtung_1", "richtung_2", "gesamt"],
        "cycle_count_15.parquet",
    )

    lat = pd.to_numeric(stations_df["latitude"], errors="coerce")
    lon = pd.to_numeric(stations_df["longitude"], errors="coerce")
    if lat.isnull().any() or lon.isnull().any():
        raise ValueError(
            "counting_stations.parquet: latitude/longitude contain non-numeric values"
        )
    if ((lat < -90) | (lat > 90)).any():
        raise ValueError(
            "counting_stations.parquet: latitude out of valid range [-90, 90]"
        )
    if ((lon < -180) | (lon > 180)).any():
        raise ValueError(
            "counting_stations.parquet: longitude out of valid range [-180, 180]"
        )

    day_stations = set(day_df["zaehlstelle"].astype(str).str.strip().unique())
    qh_stations = set(qh_df["zaehlstelle"].astype(str).str.strip().unique())
    station_meta = set(stations_df["zaehlstelle"].astype(str).str.strip().unique())

    if day_stations != qh_stations:
        raise ValueError(
            "Station mismatch between day and 15-minute counts: "
            f"only_in_day={sorted(day_stations - qh_stations)}, "
            f"only_in_15={sorted(qh_stations - day_stations)}"
        )
    if not day_stations.issubset(station_meta):
        raise ValueError(
            "Some stations in counts are missing in counting_stations metadata: "
            f"{sorted(day_stations - station_meta)}"
        )

    return _assert_daily_continuity(day_df)


def _validate_contract_file(
    file_path: Path, required_columns: set[str], dataset_name: str
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing required processed file for {dataset_name}: {file_path}"
        )
    df = pd.read_parquet(file_path)
    if df.empty:
        raise ValueError(f"{dataset_name}: file is empty: {file_path}")
    _assert_required_columns(df, required_columns, dataset_name)
    return issues


def _validate_parking_and_paths(base: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    parking_path = base / "cycle_parking" / "parking_sites.parquet"
    paths_path = base / "cycle_paths" / "path_segments.parquet"

    issues.extend(
        _validate_contract_file(
            parking_path,
            {"site_id", "latitude", "longitude", "capacity_total"},
            "cycle_parking/parking_sites.parquet",
        )
    )
    issues.extend(
        _validate_contract_file(
            paths_path,
            {"segment_id", "length_m", "surface_type", "is_protected"},
            "cycle_paths/path_segments.parquet",
        )
    )
    return issues


def run(profile: str = "local") -> None:
    issues: list[ValidationIssue] = []
    try:
        processed_base = _resolve_processed_path(profile)
        if not processed_base.exists():
            raise FileNotFoundError(
                f"Processed data path does not exist: {processed_base}"
            )

        issues.extend(_validate_cycle_counts(processed_base))
        issues.extend(_validate_parking_and_paths(processed_base))
    except Exception as exc:
        print(f"Validation FAILED: {exc}")
        raise

    if issues:
        print("Validation completed with warnings:")
        for issue in issues:
            print(f"[{issue.level}] {issue.message}")
        return

    print("Validation successful: no errors and no warnings.")


if __name__ == "__main__":
    run()
