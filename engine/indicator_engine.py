"""
==========================================
Sultan Quant Lab
Module : Indicator Engine
Version : 2.1
==========================================
"""

import pandas as pd

from indicators.ema import add_ema
from indicators.rsi import add_rsi
from indicators.atr import add_atr
from indicators.adx import add_adx
from indicators.stochastic import add_stochastic


def calculate_indicators(
    df: pd.DataFrame,
    use_ema: bool = True,
    use_rsi: bool = True,
    use_atr: bool = True,
    use_adx: bool = True,
    use_stochastic: bool = True,
) -> pd.DataFrame:

    if use_ema:
        df = add_ema(df)

    if use_rsi:
        df = add_rsi(df)

    if use_atr:
        df = add_atr(df)

    if use_adx:
        df = add_adx(df)

    if use_stochastic:
        df = add_stochastic(df)

    return df