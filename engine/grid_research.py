"""
==========================================
SULTAN QUANT OS
Module : Grid Research Engine
Version : 1.0
==========================================

Research engine for crypto grid strategies.

Purpose
-------
Analyze historical OHLC data to determine:

- MAE (Maximum Adverse Excursion)
- MFE (Maximum Favorable Excursion)
- Probability of price reaching drawdown levels
- Probability of recovery after drawdown
- Probability of reaching TP after drawdown
- Average recovery time
- Maximum excursion

Important
---------
This module is RESEARCH ONLY.

It does not place trades.

It deliberately avoids assuming the order of
high/low movement inside the same candle.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


# ============================================================
# RESULT DATACLASS
# ============================================================


@dataclass
class GridResearchResult:

    entries: int

    horizon_bars: int

    drawdown_levels: list[float]

    recovery_levels: list[float]

    mae: pd.Series

    mfe: pd.Series

    drawdown_probability: dict[float, float]

    recovery_probability: dict[float, float]

    conditional_recovery_probability: dict[
        tuple[float, float],
        float,
    ]

    average_recovery_bars: dict[
        tuple[float, float],
        float,
    ]


# ============================================================
# ENGINE
# ============================================================


class GridResearchEngine:

    def __init__(
        self,
        df: pd.DataFrame,
        horizon_bars: int = 288,
    ):
        """
        Parameters
        ----------
        df:
            OHLC DataFrame.

        horizon_bars:
            Number of future candles to inspect.

            288 candles = 24 hours on 5-minute data.
        """

        self.df = self._validate_dataframe(df)

        if horizon_bars <= 0:

            raise ValueError(
                "horizon_bars must be > 0"
            )

        self.horizon_bars = horizon_bars

    # ========================================================
    # VALIDATE DATA
    # ========================================================

    @staticmethod
    def _validate_dataframe(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        required = [
            "open",
            "high",
            "low",
            "close",
        ]

        missing = [
            column
            for column in required
            if column not in df.columns
        ]

        if missing:

            raise ValueError(
                f"Missing columns: {missing}"
            )

        result = df.copy()

        for column in required:

            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

        result = result.dropna(
            subset=required
        )

        if result.empty:

            raise ValueError(
                "DataFrame contains no valid OHLC data"
            )

        return result.reset_index(
            drop=True
        )

    # ========================================================
    # MAE
    # ========================================================

    def calculate_mae(
        self,
    ) -> pd.Series:
        """
        Calculate Maximum Adverse Excursion.

        Entry price = current candle close.

        MAE is the maximum percentage decline
        observed during the future horizon.

        Example:

            entry = 100
            future low = 97

            MAE = -3%
        """

        closes = self.df["close"].to_numpy(
            dtype=float
        )

        lows = self.df["low"].to_numpy(
            dtype=float
        )

        result = np.full(
            len(self.df),
            np.nan,
        )

        for i in range(
            len(self.df)
        ):

            end = min(
                i + self.horizon_bars + 1,
                len(self.df),
            )

            if i + 1 >= end:

                continue

            entry = closes[i]

            future_lows = lows[
                i + 1:end
            ]

            minimum = np.min(
                future_lows
            )

            result[i] = (
                minimum / entry - 1.0
            )

        return pd.Series(
            result,
            index=self.df.index,
            name="MAE",
        )

    # ========================================================
    # MFE
    # ========================================================

    def calculate_mfe(
        self,
    ) -> pd.Series:
        """
        Calculate Maximum Favorable Excursion.

        Entry price = current candle close.

        MFE is the maximum percentage rise
        observed during the future horizon.
        """

        closes = self.df["close"].to_numpy(
            dtype=float
        )

        highs = self.df["high"].to_numpy(
            dtype=float
        )

        result = np.full(
            len(self.df),
            np.nan,
        )

        for i in range(
            len(self.df)
        ):

            end = min(
                i + self.horizon_bars + 1,
                len(self.df),
            )

            if i + 1 >= end:

                continue

            entry = closes[i]

            future_highs = highs[
                i + 1:end
            ]

            maximum = np.max(
                future_highs
            )

            result[i] = (
                maximum / entry - 1.0
            )

        return pd.Series(
            result,
            index=self.df.index,
            name="MFE",
        )

    # ========================================================
    # DRAW DOWN PROBABILITY
    # ========================================================

    def calculate_drawdown_probability(
        self,
        mae: pd.Series,
        levels: list[float],
    ) -> dict[float, float]:
        """
        Probability that price reaches
        a specified drawdown.

        levels are positive percentages.

        Example:

            0.01 = 1%
        """

        result = {}

        valid = mae.dropna()

        if valid.empty:

            return {
                level: 0.0
                for level in levels
            }

        for level in levels:

            if level <= 0:

                raise ValueError(
                    "Drawdown levels must be > 0"
                )

            result[level] = float(
                (
                    valid <= -level
                ).mean()
                * 100.0
            )

        return result

    # ========================================================
    # RECOVERY AFTER DRAWDOWN
    # ========================================================

    def calculate_conditional_recovery(
        self,
        drawdown_levels: list[float],
        recovery_levels: list[float],
    ) -> tuple[
        dict[tuple[float, float], float],
        dict[tuple[float, float], float],
    ]:
        """
        Conditional recovery probability.

        Logic:

        1. Entry at candle close.
        2. Future price first reaches drawdown.
        3. ONLY AFTER that candle, inspect subsequent candles.
        4. Determine whether price reaches recovery level.

        This avoids assuming the order of high/low
        within a single candle.

        Example:

            drawdown = 1%
            recovery = 1%

        Means:

            price first falls >= 1%
            THEN subsequently rises >= 1%
            from the original entry price.
        """

        closes = self.df["close"].to_numpy(
            dtype=float
        )

        highs = self.df["high"].to_numpy(
            dtype=float
        )

        lows = self.df["low"].to_numpy(
            dtype=float
        )

        probabilities = {}

        recovery_bars = {}

        total_entries = len(
            self.df
        )

        for dd in drawdown_levels:

            if dd <= 0:

                raise ValueError(
                    "Drawdown levels must be > 0"
                )

            for recovery in recovery_levels:

                if recovery <= 0:

                    raise ValueError(
                        "Recovery levels must be > 0"
                    )

                key = (
                    dd,
                    recovery,
                )

                drawdown_count = 0

                recovery_count = 0

                recovery_times = []

                for i in range(
                    total_entries
                ):

                    end = min(
                        i
                        + self.horizon_bars
                        + 1,
                        total_entries,
                    )

                    if i + 1 >= end:

                        continue

                    entry = closes[i]

                    drawdown_price = (
                        entry
                        * (1.0 - dd)
                    )

                    recovery_price = (
                        entry
                        * (1.0 + recovery)
                    )

                    drawdown_index = None

                    # ======================================
                    # FIND FIRST DRAWDOWN
                    # ======================================

                    for j in range(
                        i + 1,
                        end,
                    ):

                        if (
                            lows[j]
                            <= drawdown_price
                        ):

                            drawdown_index = j

                            break

                    if drawdown_index is None:

                        continue

                    drawdown_count += 1

                    # ======================================
                    # RECOVERY MUST HAPPEN AFTER
                    # DRAWDOWN CANDLE
                    # ======================================

                    recovery_index = None

                    for j in range(
                        drawdown_index + 1,
                        end,
                    ):

                        if (
                            highs[j]
                            >= recovery_price
                        ):

                            recovery_index = j

                            break

                    if recovery_index is not None:

                        recovery_count += 1

                        recovery_times.append(
                            recovery_index
                            - drawdown_index
                        )

                if drawdown_count == 0:

                    probabilities[key] = 0.0

                    recovery_bars[key] = np.nan

                else:

                    probabilities[key] = (
                        recovery_count
                        / drawdown_count
                        * 100.0
                    )

                    if recovery_times:

                        recovery_bars[key] = (
                            float(
                                np.mean(
                                    recovery_times
                                )
                            )
                        )

                    else:

                        recovery_bars[key] = np.nan

        return (
            probabilities,
            recovery_bars,
        )

    # ========================================================
    # FULL RESEARCH
    # ========================================================

    def research(
        self,
        drawdown_levels: list[float],
        recovery_levels: list[float],
    ) -> GridResearchResult:

        mae = self.calculate_mae()

        mfe = self.calculate_mfe()

        drawdown_probability = (
            self.calculate_drawdown_probability(
                mae,
                drawdown_levels,
            )
        )

        (
            recovery_probability,
            average_recovery_bars,
        ) = self.calculate_conditional_recovery(
            drawdown_levels,
            recovery_levels,
        )

        valid_entries = (
            mae.notna()
        )

        return GridResearchResult(

            entries=int(
                valid_entries.sum()
            ),

            horizon_bars=self.horizon_bars,

            drawdown_levels=(
                drawdown_levels.copy()
            ),

            recovery_levels=(
                recovery_levels.copy()
            ),

            mae=mae,

            mfe=mfe,

            drawdown_probability=(
                drawdown_probability
            ),

            recovery_probability=(
                recovery_probability
            ),

            conditional_recovery_probability=(
                recovery_probability
            ),

            average_recovery_bars=(
                average_recovery_bars
            ),
        )


# ============================================================
# REPORT HELPER
# ============================================================


def print_research_report(
    result: GridResearchResult,
) -> None:

    print()
    print("=" * 70)
    print("SULTAN QUANT OS - GRID RESEARCH")
    print("=" * 70)

    print(
        f"Entries        : {result.entries:,}"
    )

    print(
        f"Horizon        : "
        f"{result.horizon_bars} candles"
    )

    print()
    print("DRAW-DOWN PROBABILITY")
    print("-" * 70)

    for level in result.drawdown_levels:

        probability = (
            result.drawdown_probability[
                level
            ]
        )

        print(
            f"-{level * 100:.2f}%"
            f" -> {probability:6.2f}%"
        )

    print()
    print("CONDITIONAL RECOVERY PROBABILITY")
    print("-" * 70)

    for dd in result.drawdown_levels:

        for recovery in result.recovery_levels:

            key = (
                dd,
                recovery,
            )

            probability = (
                result.recovery_probability[
                    key
                ]
            )

            bars = (
                result.average_recovery_bars[
                    key
                ]
            )

            if np.isnan(bars):

                bars_text = "N/A"

            else:

                bars_text = (
                    f"{bars:.1f} bars"
                )

            print(
                f"DD -{dd * 100:.2f}%"
                f" -> TP +{recovery * 100:.2f}%"
                f" : {probability:6.2f}%"
                f" | avg {bars_text}"
            )

    print()
    print("=" * 70)