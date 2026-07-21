"""
==========================================
Sultan Quant Lab
Module : ADX Indicator
Version : 2.1
==========================================
"""

from ta.trend import ADXIndicator
import config.settings as settings


def add_adx(df):
    """
    Menambahkan indikator ADX ke DataFrame.
    """

    required_columns = ["high", "low", "close"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Kolom '{column}' tidak ditemukan."
            )

    adx = ADXIndicator(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=settings.ADX_PERIOD,
    )

    df["ADX"] = adx.adx()

    return df