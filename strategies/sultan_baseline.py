"""
==========================================
SULTAN QUANT OS
Sultan Baseline Strategy
Version : 1.0.0
==========================================

Responsibilities:

- EMA Trend Filter
- RSI Pullback
- Stochastic Confirmation
- ADX Trend Filter
- ATR Risk Management

"""

from strategies.base_strategy import initialize_strategy
from strategies.signal_builder import (
    set_buy,
    set_sell,
    finish,
)
from strategies.risk_builder import (
    calculate_buy_levels,
    calculate_sell_levels,
)


# ==================================================
# GENERATE SIGNAL
# ==================================================

def generate_signal(df):

    df = initialize_strategy(df)

    for i in range(1, len(df)):

        row = df.iloc[i]

        close = row["close"]
        atr = row["ATR"]

        # ==========================================
        # BUY
        # ==========================================

        if (

            row["EMA20"] > row["EMA50"]
            and row["EMA50"] > row["EMA200"]

            and row["RSI"] < 10

            and row["%K"] < 20

            and row["ADX"] >= 25

        ):

            sl, tp = calculate_buy_levels(

                entry=close,
                atr=atr,
                sl_multiplier=1.0,
                rr=2.0,

            )

            set_buy(

                df,
                i,
                sl,
                tp,

            )

        # ==========================================
        # SELL
        # ==========================================

        elif (

            row["EMA20"] < row["EMA50"]
            and row["EMA50"] < row["EMA200"]

            and row["RSI"] > 90

            and row["%K"] > 80

            and row["ADX"] >= 25

        ):

            sl, tp = calculate_sell_levels(

                entry=close,
                atr=atr,
                sl_multiplier=1.0,
                rr=2.0,

            )

            set_sell(

                df,
                i,
                sl,
                tp,

            )

    return finish(df)