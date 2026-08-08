import pandas as pd

from forecast_app.data.schemas import (
    CountingStationsContract,
    CycleCount15Contract,
    CycleCountDayContract,
    validate_dataframe_contract,
)


def test_validate_dataframe_contract_accepts_valid_cycle_count_rows() -> None:
    df = pd.DataFrame(
        [
            {
                "datum": "2024.01.01",
                "uhrzeit_start": "00:00",
                "uhrzeit_ende": "00:15",
                "zaehlstelle": "Arnulf",
                "richtung_1": 2.0,
                "richtung_2": 1.0,
                "gesamt": 3.0,
            }
        ]
    )

    validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")


def test_validate_dataframe_contract_detects_missing_station_column() -> None:
    df = pd.DataFrame(
        [
            {
                "datum": "2024.01.01",
                "uhrzeit_start": "00:00",
                "uhrzeit_ende": "00:15",
                "station_id": "Arnulf",
                "richtung_1": 2.0,
                "richtung_2": 1.0,
                "gesamt": 3.0,
            }
        ]
    )

    try:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    except ValueError as exc:
        assert "zaehlstelle" in str(exc)
    else:
        raise AssertionError(
            "Expected schema validation to fail for renamed station column"
        )


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

    try:
        validate_dataframe_contract(df, CountingStationsContract, "counting_stations")
    except ValueError as exc:
        assert "latitude" in str(exc)
    else:
        raise AssertionError(
            "Expected schema validation to fail for out-of-bounds coordinates"
        )


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


def test_validate_dataframe_contract_distinguishes_missing_numeric_value() -> None:
    df = pd.DataFrame(
        [
            {
                "datum": "2024.01.01",
                "uhrzeit_start": "00:00",
                "uhrzeit_ende": "00:15",
                "zaehlstelle": "Arnulf",
                "richtung_1": 2.0,
                "richtung_2": None,
                "gesamt": 3.0,
            }
        ]
    )

    try:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    except ValueError as exc:
        message = str(exc)
        assert "missing numeric values" in message
        assert "richtung_2" in message
    else:
        raise AssertionError(
            "Expected schema validation to fail for missing numeric value"
        )


def test_validate_dataframe_contract_distinguishes_invalid_numeric_value() -> None:
    df = pd.DataFrame(
        [
            {
                "datum": "2024.01.01",
                "uhrzeit_start": "00:00",
                "uhrzeit_ende": "00:15",
                "zaehlstelle": "Arnulf",
                "richtung_1": 2.0,
                "richtung_2": "banana",
                "gesamt": 3.0,
            }
        ]
    )

    try:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    except ValueError as exc:
        message = str(exc)
        assert "invalid numeric values" in message
        assert "banana" in message
    else:
        raise AssertionError(
            "Expected schema validation to fail for invalid numeric value"
        )


def test_validate_dataframe_contract_treats_missing_text_tokens_as_missing() -> None:
    df = pd.DataFrame(
        [
            {
                "datum": "2024.01.01",
                "uhrzeit_start": "00:00",
                "uhrzeit_ende": "00:15",
                "zaehlstelle": "Arnulf",
                "richtung_1": 2.0,
                "richtung_2": "N/A",
                "gesamt": 3.0,
            }
        ]
    )

    try:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    except ValueError as exc:
        message = str(exc)
        assert "missing numeric values" in message
    else:
        raise AssertionError("Expected schema validation to fail for missing token")


def test_validate_dataframe_contract_detects_invalid_numeric_type() -> None:
    df = pd.DataFrame(
        [
            {
                "datum": "2024.01.01",
                "uhrzeit_start": "00:00",
                "uhrzeit_ende": "00:15",
                "zaehlstelle": "Arnulf",
                "richtung_1": 2.0,
                "richtung_2": {"bad": "value"},
                "gesamt": 3.0,
            }
        ]
    )

    try:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    except ValueError as exc:
        message = str(exc)
        assert "invalid numeric types" in message
        assert "dict" in message
    else:
        raise AssertionError("Expected schema validation to fail for invalid type")


def test_validate_dataframe_contract_detects_non_string_value() -> None:
    df = pd.DataFrame(
        [
            {
                "datum": 20240101,
                "uhrzeit_start": "00:00",
                "uhrzeit_ende": "00:15",
                "zaehlstelle": "Arnulf",
                "richtung_1": 2.0,
                "richtung_2": 1.0,
                "gesamt": 3.0,
            }
        ]
    )

    try:
        validate_dataframe_contract(df, CycleCount15Contract, "cycle_count_15")
    except ValueError as exc:
        message = str(exc)
        assert "non-string values" in message
        assert "datum" in message
    else:
        raise AssertionError("Expected schema validation to fail for non-string value")
