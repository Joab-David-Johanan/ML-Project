import pandas as pd
import pytest

from forecast_app.data.schemas import (
    CountingStationsContract,
    CycleCount15Contract,
    CycleCountDayContract,
    validate_dataframe_contract,
)


@pytest.fixture
def valid_cycle_count_15_row() -> dict[str, object]:
    return {
        "datum": "2024.01.01",
        "uhrzeit_start": "00:00",
        "uhrzeit_ende": "00:15",
        "zaehlstelle": "Arnulf",
        "richtung_1": 2.0,
        "richtung_2": 1.0,
        "gesamt": 3.0,
    }


def _build_df(
    base_row: dict[str, object],
    overrides: dict[str, object] | None = None,
    drop_keys: set[str] | None = None,
) -> pd.DataFrame:
    row = dict(base_row)
    if overrides:
        row.update(overrides)
    if drop_keys:
        for key in drop_keys:
            row.pop(key, None)
    return pd.DataFrame([row])


def test_validate_dataframe_contract_accepts_valid_cycle_count_rows(
    valid_cycle_count_15_row: dict[str, object],
) -> None:
    df = _build_df(valid_cycle_count_15_row)

    validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")


def test_validate_dataframe_contract_detects_missing_station_column(
    valid_cycle_count_15_row: dict[str, object],
) -> None:
    df = _build_df(
        valid_cycle_count_15_row,
        overrides={"station_id": "Arnulf"},
        drop_keys={"zaehlstelle"},
    )

    with pytest.raises(ValueError, match="zaehlstelle"):
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")


def test_validate_dataframe_contract_detects_invalid_station_coordinates() -> None:
    df = pd.DataFrame(
        [
            {
                "zaehlstelle": "Arnulf",
                "zaehlstelle_lang": "Arnulfstr.",
                "latitude": 95.0,
                "longitude": 11.55,
                "richtung_1": "Ost",
                "richtung_2": "West",
                "besonderheiten": "ok",
            }
        ]
    )

    with pytest.raises(ValueError, match="latitude"):
        validate_dataframe_contract(df, CountingStationsContract, "counting_stations")


def test_validate_dataframe_contract_accepts_valid_daily_counts() -> None:
    df = pd.DataFrame(
        [
            {
                "datum": "2024.01.01",
                "uhrzeit_start": "00:00",
                "uhrzeit_ende": "23:59",
                "zaehlstelle": "Arnulf",
                "richtung_1": 2.0,
                "richtung_2": 1.0,
                "gesamt": 3.0,
            }
        ]
    )

    validate_dataframe_contract(df, CycleCountDayContract, "cycle_count_day")


def test_validate_dataframe_contract_distinguishes_missing_numeric_value(
    valid_cycle_count_15_row: dict[str, object],
) -> None:
    df = _build_df(valid_cycle_count_15_row, overrides={"richtung_2": None})

    with pytest.raises(ValueError, match="missing numeric values"):
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")


def test_validate_dataframe_contract_distinguishes_invalid_numeric_value(
    valid_cycle_count_15_row: dict[str, object],
) -> None:
    df = _build_df(valid_cycle_count_15_row, overrides={"richtung_2": "banana"})

    with pytest.raises(ValueError, match="invalid numeric values") as exc_info:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    assert "banana" in str(exc_info.value)


def test_validate_dataframe_contract_treats_missing_text_tokens_as_missing(
    valid_cycle_count_15_row: dict[str, object],
) -> None:
    df = _build_df(valid_cycle_count_15_row, overrides={"richtung_2": "N/A"})

    with pytest.raises(ValueError, match="missing numeric values"):
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")


def test_validate_dataframe_contract_detects_invalid_numeric_type(
    valid_cycle_count_15_row: dict[str, object],
) -> None:
    df = _build_df(valid_cycle_count_15_row, overrides={"richtung_2": {"bad": "value"}})

    with pytest.raises(ValueError, match="invalid numeric types") as exc_info:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    assert "dict" in str(exc_info.value)


def test_validate_dataframe_contract_detects_non_string_value(
    valid_cycle_count_15_row: dict[str, object],
) -> None:
    df = _build_df(valid_cycle_count_15_row, overrides={"datum": 20240101})

    with pytest.raises(ValueError, match="non-string values") as exc_info:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    assert "datum" in str(exc_info.value)
