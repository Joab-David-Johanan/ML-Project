from __future__ import annotations

# Import Iterable for type hints on lists of input files.
from collections.abc import Iterable

# Import pathlib so file paths are handled safely across operating systems.
from pathlib import Path

# Import pandas for CSV loading, cleaning, merging, and Parquet export.
import pandas as pd

# Root folder containing cycle count raw files organized by year folders.
RAW_COUNTS_DIR = Path("data/raw/cycle_counts")
# Folder where merged intermediate outputs are written.
INTERIM_COUNTS_DIR = Path("data/interim/cycle_counts")
# Historical folder that already contains combined files for 2017-2024.
HISTORICAL_DIR = RAW_COUNTS_DIR / "2017_2024"
# Canonical counting station metadata file with location reference.
COUNTING_STATIONS_FILE = HISTORICAL_DIR / "counting_stations.csv"
# Monthly folders to merge after historical data.
YEARS = ("2025", "2026")


# Build the sorted list of monthly files for a given year and suffix.
def _monthly_files(year: str, suffix: str) -> list[Path]:
    # Resolve the folder for one year, for example data/raw/cycle_counts/2025.
    year_dir = RAW_COUNTS_DIR / year
    # Match file names like rad_2025_03_15min.csv or rad_2025_03_tage.csv.
    return sorted(year_dir.glob(f"rad_{year}_*_{suffix}.csv"))


# Normalize one dataframe so all inputs share consistent schema formatting.
def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Copy input to avoid mutating the original dataframe object.
    df = df.copy()
    # Strip accidental whitespace around all column names.
    df.columns = [c.strip() for c in df.columns]

    # Trim leading/trailing whitespace in common text columns.
    for text_col in ("datum", "uhrzeit_start", "uhrzeit_ende", "zaehlstelle"):
        # Only process columns that actually exist in the current file.
        if text_col in df.columns:
            # Cast to string and trim spaces to standardize values.
            df[text_col] = df[text_col].astype(str).str.strip()

    # Normalize date text into compact yyyy.mm.dd format.
    if "datum" in df.columns:
        # Remove all spaces that may appear inside date values.
        df["datum"] = df["datum"].str.replace(" ", "", regex=False)

    # Normalize time strings into hh:mm format.
    for time_col in ("uhrzeit_start", "uhrzeit_ende"):
        # Only normalize when this time column exists.
        if time_col in df.columns:
            # Convert 23.59 style values to 23:59 for consistency.
            df[time_col] = df[time_col].str.replace(".", ":", regex=False)

    # List all numeric fields that should be converted to numeric types.
    numeric_cols = (
        "richtung_1",
        "richtung_2",
        "gesamt",
        "min-temp",
        "max-temp",
        "niederschlag",
        "bewoelkung",
        "sonnenstunden",
    )
    # Convert numeric columns safely, coercing invalid values to NaN.
    for col in numeric_cols:
        # Convert only if column exists in the current dataset.
        if col in df.columns:
            # Parse numeric values and mark invalid tokens as missing.
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Track required identifier columns used for joins and grouping.
    required_cols = [c for c in ("datum", "zaehlstelle") if c in df.columns]
    # Drop rows where required identifier columns are missing.
    if required_cols:
        df = df.dropna(subset=required_cols)

    # Return normalized dataframe.
    return df


# Read and merge a list of CSV files into one cleaned dataframe.
def _merge_files(csv_files: Iterable[Path]) -> pd.DataFrame:
    # Collect normalized dataframes before concatenation.
    frames: list[pd.DataFrame] = []
    # Iterate through each input CSV path.
    for file_path in csv_files:
        # Read one CSV file into memory.
        frame = pd.read_csv(file_path)
        # Normalize column names, text formatting, and numeric fields.
        frame = _normalize_dataframe(frame)
        # Append cleaned frame for later concatenation.
        frames.append(frame)

    # Return empty dataframe if no files were passed.
    if not frames:
        return pd.DataFrame()

    # Stack all frames vertically and reset row indices.
    merged = pd.concat(frames, ignore_index=True)
    # Remove exact duplicate rows across source files.
    merged = merged.drop_duplicates()

    # Sort by natural keys when columns are available.
    sort_cols = [
        c for c in ("datum", "zaehlstelle", "uhrzeit_start") if c in merged.columns
    ]
    # Apply sorting only if at least one sort column exists.
    if sort_cols:
        # Sort and reset index for deterministic output files.
        merged = merged.sort_values(sort_cols).reset_index(drop=True)

    # Return merged and cleaned dataframe.
    return merged


# Write one dataframe as Parquet in the interim output folder.
def _write_outputs(df: pd.DataFrame, basename: str) -> None:
    # Ensure output directory exists before writing files.
    INTERIM_COUNTS_DIR.mkdir(parents=True, exist_ok=True)

    # Build output Parquet path.
    parquet_path = INTERIM_COUNTS_DIR / f"{basename}.parquet"

    # Write Parquet output only for efficient downstream processing.
    df.to_parquet(parquet_path, index=False)


# Load and export counting station metadata into interim outputs.
def _export_counting_stations() -> None:
    # Skip export gracefully when source metadata file is missing.
    if not COUNTING_STATIONS_FILE.exists():
        print("Counting stations metadata file not found; skipping export.")
        return

    # Read counting station metadata and strip accidental column whitespace.
    stations = pd.read_csv(COUNTING_STATIONS_FILE)
    stations.columns = [c.strip() for c in stations.columns]

    # Trim whitespace in text-like columns for stable joins.
    for col in stations.columns:
        if stations[col].dtype == object:
            stations[col] = stations[col].astype(str).str.strip()

    # Write normalized station metadata to interim Parquet.
    _write_outputs(stations, "counting_stations")
    print(f"Exported counting stations rows: {len(stations)}")


# Build the full list of 15-minute input files across all target years.
def _all_15min_files() -> list[Path]:
    # Start with historical combined file for 2017-2024.
    files: list[Path] = [HISTORICAL_DIR / "cycle_count_15min.csv"]
    # Add all monthly files for 2025 and 2026.
    for year in YEARS:
        files.extend(_monthly_files(year, "15min"))
    # Keep only files that actually exist on disk.
    return [p for p in files if p.exists()]


# Build the full list of daily input files across all target years.
def _all_day_files() -> list[Path]:
    # Start with historical combined daily file for 2017-2024.
    files: list[Path] = [HISTORICAL_DIR / "cycle_count_day.csv"]
    # Add all monthly daily/weather files for 2025 and 2026.
    for year in YEARS:
        files.extend(_monthly_files(year, "tage"))
    # Keep only files that actually exist on disk.
    return [p for p in files if p.exists()]


# Pipeline entrypoint used by pipelines/run_ingest.py.
def run() -> None:
    # Export station metadata because it is needed for location joins.
    _export_counting_stations()

    # Resolve full input file lists for both granularities.
    files_15min = _all_15min_files()
    files_day = _all_day_files()

    # Merge all 15-minute files into one normalized dataframe.
    merged_15min = _merge_files(files_15min)
    # Merge all daily files into one normalized dataframe.
    merged_day = _merge_files(files_day)

    # Handle the 15-minute output branch.
    if merged_15min.empty:
        # Print a warning when no 15-minute data could be loaded.
        print("No 15-minute files found for 2017-2026 merge.")
    else:
        # Write unified 15-minute dataset to interim Parquet.
        _write_outputs(merged_15min, "cycle_count_15")
        # Print row count for verification and logging.
        print(f"Merged 15-minute rows: {len(merged_15min)}")

    # Handle the daily output branch.
    if merged_day.empty:
        # Print a warning when no daily data could be loaded.
        print("No daily files found for 2017-2026 merge.")
    else:
        # Write unified daily dataset to interim Parquet.
        _write_outputs(merged_day, "cycle_count_day")
        # Print row count for verification and logging.
        print(f"Merged daily rows: {len(merged_day)}")
