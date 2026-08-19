import pandas as pd

from engine.bitget_loader import (
    OUTPUT_COLUMNS,
    _normalize_candles,
)


def test_normalize_bitget_candles():

    raw = [
        [
            "1786758000000",
            "56.547",
            "56.548",
            "56.503",
            "56.513",
            "70.4",
            "3979.52438",
            "3979.52438",
        ]
    ]

    df = _normalize_candles(raw)

    assert list(df.columns) == OUTPUT_COLUMNS

    assert len(df) == 1

    assert isinstance(
        df["time"].iloc[0],
        pd.Timestamp,
    )

    assert df["open"].iloc[0] == 56.547

    assert df["high"].iloc[0] == 56.548

    assert df["low"].iloc[0] == 56.503

    assert df["close"].iloc[0] == 56.513

    assert df["volume"].iloc[0] == 70.4


def test_normalize_empty_data():

    df = _normalize_candles([])

    assert df.empty

    assert list(df.columns) == OUTPUT_COLUMNS


def test_normalize_removes_duplicates():

    row = [
        "1786758000000",
        "56.547",
        "56.548",
        "56.503",
        "56.513",
        "70.4",
        "3979.52438",
        "3979.52438",
    ]

    df = _normalize_candles(
        [row, row]
    )

    assert len(df) == 1