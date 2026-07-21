"""
==========================================
Sultan Quant Lab
Module : Data Loader
Version : 2.1
==========================================
"""

from pathlib import Path
import pandas as pd


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load historical data from MT5 CSV.
    """

    file = Path(file_path)

    if not file.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}"
        )

    df = pd.read_csv(file)

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    required_columns = [
        "time",
        "open",
        "high",
        "low",
        "close",
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    df["time"] = pd.to_datetime(df["time"])

    df.sort_values(
        "time",
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    return df