from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DataFrameContract:
    name: str
    required_columns: tuple[str, ...]
    column_types: dict[str, str]
    numeric_constraints: dict[str, tuple[float | None, float | None]] | None = None


CycleCount15Contract = DataFrameContract(
    name="cycle_count_15",
    required_columns=(
        "datum",
        "uhrzeit_start",
        "uhrzeit_ende",
        "zaehlstelle",
        "richtung_1",
        "richtung_2",
        "gesamt",
    ),
    column_types={
        "datum": "string",
        "uhrzeit_start": "string",
        "uhrzeit_ende": "string",
        "zaehlstelle": "string",
        "richtung_1": "number",
        "richtung_2": "number",
        "gesamt": "number",
    },
    numeric_constraints={
        "richtung_1": (0.0, None),
        "richtung_2": (0.0, None),
        "gesamt": (0.0, None),
    },
)


CycleCountDayContract = DataFrameContract(
    name="cycle_count_day",
    required_columns=(
        "datum",
        "uhrzeit_start",
        "uhrzeit_ende",
        "zaehlstelle",
        "richtung_1",
        "richtung_2",
        "gesamt",
    ),
    column_types={
        "datum": "string",
        "uhrzeit_start": "string",
        "uhrzeit_ende": "string",
        "zaehlstelle": "string",
        "richtung_1": "number",
        "richtung_2": "number",
        "gesamt": "number",
    },
    numeric_constraints={
        "richtung_1": (0.0, None),
        "richtung_2": (0.0, None),
        "gesamt": (0.0, None),
    },
)


CountingStationsContract = DataFrameContract(
    name="counting_stations",
    required_columns=(
        "zaehlstelle",
        "zaehlstelle_lang",
        "latitude",
        "longitude",
        "richtung_1",
        "richtung_2",
        "besonderheiten",
    ),
    column_types={
        "zaehlstelle": "string",
        "zaehlstelle_lang": "string",
        "latitude": "number",
        "longitude": "number",
        "richtung_1": "string",
        "richtung_2": "string",
        "besonderheiten": "string",
    },
    numeric_constraints={"latitude": (-90.0, 90.0), "longitude": (-180.0, 180.0)},
)


MISSING_TEXT_TOKENS = {"", "na", "n/a", "none", "null", "nan", "missing"}


def _is_missing_text_value(value: object) -> bool:
    return isinstance(value, str) and value.strip().lower() in MISSING_TEXT_TOKENS


def _is_invalid_numeric_type(value: object) -> bool:
    # bool is intentionally treated as invalid for measurement columns.
    return isinstance(value, (bool, np.bool_, dict, list, tuple, set, bytes))


def _coerce_numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _validate_numeric_column(
    series: pd.Series, dataset_name: str, column: str
) -> pd.Series:
    missing_text_mask = series.map(_is_missing_text_value)
    missing_mask = series.isna() | missing_text_mask

    invalid_type_mask = series.map(_is_invalid_numeric_type) & ~missing_mask

    normalized = series.where(~missing_text_mask, pd.NA)
    coerced = _coerce_numeric_series(normalized)
    invalid_value_mask = coerced.isna() & ~missing_mask & ~invalid_type_mask

    missing_count = int(missing_mask.sum())
    invalid_type_count = int(invalid_type_mask.sum())
    invalid_value_count = int(invalid_value_mask.sum())

    if missing_count > 0:
        raise ValueError(
            f"{dataset_name}: column '{column}' contains missing numeric values ({missing_count})"
        )
    if invalid_type_count > 0:
        bad_examples = sorted(
            {
                type(value).__name__
                for value in series[invalid_type_mask].dropna().head(3).tolist()
            }
        )
        raise ValueError(
            f"{dataset_name}: column '{column}' contains invalid numeric types "
            f"({invalid_type_count}); examples={bad_examples}"
        )
    if invalid_value_count > 0:
        bad_examples = sorted(
            {
                str(value)
                for value in series[invalid_value_mask].dropna().head(3).tolist()
            }
        )
        raise ValueError(
            f"{dataset_name}: column '{column}' contains invalid numeric values "
            f"({invalid_value_count}); examples={bad_examples}"
        )

    return coerced


def _validate_string_column(
    series: pd.Series, dataset_name: str, column: str
) -> pd.Series:
    missing_text_mask = series.map(_is_missing_text_value)
    missing_mask = series.isna() | missing_text_mask
    missing_count = int(missing_mask.sum())
    if missing_count > 0:
        raise ValueError(
            f"{dataset_name}: column '{column}' contains missing string values ({missing_count})"
        )

    invalid_type_mask = ~series.map(lambda value: isinstance(value, str))
    invalid_type_count = int(invalid_type_mask.sum())
    if invalid_type_count > 0:
        bad_examples = sorted(
            {
                type(value).__name__
                for value in series[invalid_type_mask].dropna().head(3).tolist()
            }
        )
        raise ValueError(
            f"{dataset_name}: column '{column}' contains non-string values "
            f"({invalid_type_count}); examples={bad_examples}"
        )

    return series


def validate_dataframe_contract(
    df: pd.DataFrame, contract: DataFrameContract, dataset_name: str
) -> None:
    missing_columns = [
        col for col in contract.required_columns if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"{dataset_name}: missing required columns: {missing_columns}")

    for column, expected_type in contract.column_types.items():
        if expected_type == "number":
            df[column] = _validate_numeric_column(df[column], dataset_name, column)
        elif expected_type == "string":
            df[column] = _validate_string_column(df[column], dataset_name, column)

    if contract.numeric_constraints:
        for column, (lower, upper) in contract.numeric_constraints.items():
            values = df[column]
            if lower is not None and (values < lower).any():
                raise ValueError(
                    f"{dataset_name}: column '{column}' has values below {lower}"
                )
            if upper is not None and (values > upper).any():
                raise ValueError(
                    f"{dataset_name}: column '{column}' has values above {upper}"
                )
