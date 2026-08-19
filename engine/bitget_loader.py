"""
==========================================
Sultan Quant Lab
Module : Bitget Market Data Loader
Version : 1.0
==========================================

Responsibilities:

- Download public Bitget Spot OHLCV data
- Support historical pagination
- Normalize Bitget data to SultanQuantLab format
- Save market data to CSV
- No API key required
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import time

import pandas as pd
import requests


BITGET_SPOT_CANDLE_URL = (
    "https://api.bitget.com/api/v2/spot/market/history-candles"
)

DEFAULT_SYMBOL = "HYPEUSDT"
DEFAULT_GRANULARITY = "5min"

BITGET_LIMIT = 200

OUTPUT_COLUMNS = [
    "time",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


def _request_candles(
    symbol: str,
    granularity: str,
    end_time_ms: int,
    limit: int = BITGET_LIMIT,
    timeout: int = 30,
    retries: int = 3,
) -> list:
    """
    Request one page of historical candles from Bitget.
    """

    params = {
        "symbol": symbol,
        "granularity": granularity,
        "endTime": str(end_time_ms),
        "limit": str(limit),
    }

    last_error = None

    for attempt in range(retries):

        try:
            response = requests.get(
                BITGET_SPOT_CANDLE_URL,
                params=params,
                timeout=timeout,
            )

            response.raise_for_status()

            payload = response.json()

            if payload.get("code") != "00000":
                raise RuntimeError(
                    "Bitget API error: "
                    f"{payload.get('code')} - "
                    f"{payload.get('msg')}"
                )

            return payload.get("data", [])

        except (
            requests.RequestException,
            ValueError,
            RuntimeError,
        ) as exc:

            last_error = exc

            if attempt < retries - 1:
                time.sleep(1.0 * (attempt + 1))

    raise RuntimeError(
        f"Failed to retrieve Bitget candles: {last_error}"
    )


def _normalize_candles(raw_data: list) -> pd.DataFrame:
    """
    Convert raw Bitget candle rows into
    SultanQuantLab standard OHLCV format.
    """

    if not raw_data:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    rows = []

    for row in raw_data:

        if len(row) < 6:
            continue

        rows.append(
            {
                "time": pd.to_datetime(
                    int(row[0]),
                    unit="ms",
                    utc=True,
                ),
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5]),
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    df = df.drop_duplicates(
        subset=["time"]
    )

    df = df.sort_values(
        "time"
    )

    df = df.reset_index(
        drop=True
    )

    return df[OUTPUT_COLUMNS]


def download_bitget_history(
    symbol: str = DEFAULT_SYMBOL,
    granularity: str = DEFAULT_GRANULARITY,
    days: int = 180,
    pause_seconds: float = 0.15,
) -> pd.DataFrame:
    """
    Download historical Bitget Spot candles.

    Parameters
    ----------
    symbol:
        Trading symbol, e.g. HYPEUSDT.

    granularity:
        Bitget candle interval, e.g. 5min.

    days:
        Number of historical days.

    pause_seconds:
        Delay between API requests.

    Returns
    -------
    pandas.DataFrame
        Standard SultanQuantLab OHLCV format.
    """

    if days <= 0:
        raise ValueError(
            "days must be greater than zero"
        )

    now = datetime.now(timezone.utc)

    start = now - timedelta(days=days)

    start_ms = int(
        start.timestamp() * 1000
    )

    end_ms = int(
        now.timestamp() * 1000
    )

    collected = []

    while end_ms > start_ms:

        raw_page = _request_candles(
            symbol=symbol,
            granularity=granularity,
            end_time_ms=end_ms,
        )

        if not raw_page:
            break

        collected.extend(raw_page)

        timestamps = [
            int(row[0])
            for row in raw_page
            if len(row) >= 1
        ]

        if not timestamps:
            break

        oldest_timestamp = min(
            timestamps
        )

        if oldest_timestamp <= start_ms:
            break

        end_ms = oldest_timestamp - 1

        time.sleep(
            pause_seconds
        )

    df = _normalize_candles(
        collected
    )

    if df.empty:
        return df

    df = df[
        df["time"] >= pd.Timestamp(
            start,
        )
    ]

    df = df.reset_index(
        drop=True
    )

    return df


def save_bitget_history(
    df: pd.DataFrame,
    file_path: str | Path,
) -> Path:
    """
    Save normalized Bitget OHLCV data to CSV.
    """

    file = Path(file_path)

    file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    missing = [
        column
        for column in OUTPUT_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    df[
        OUTPUT_COLUMNS
    ].to_csv(
        file,
        index=False,
    )

    return file


def download_and_save(
    symbol: str = DEFAULT_SYMBOL,
    granularity: str = DEFAULT_GRANULARITY,
    days: int = 180,
    output_path: str | Path = (
        "data/bitget/HYPEUSDT_5m.csv"
    ),
) -> Path:
    """
    Download Bitget history and save it.
    """

    df = download_bitget_history(
        symbol=symbol,
        granularity=granularity,
        days=days,
    )

    if df.empty:
        raise RuntimeError(
            "Bitget returned no candle data."
        )

    return save_bitget_history(
        df,
        output_path,
    )


if __name__ == "__main__":

    output = download_and_save()

    print("=" * 60)
    print("BITGET DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"Output : {output}")
    print(f"Candles: {len(pd.read_csv(output)):,}")