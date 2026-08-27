"""
==========================================
SULTAN QUANT OS
Module : Crypto Quality Analyzer
Version : 1.0.0
==========================================

Evaluate crypto assets using normalized scores.

This module is intentionally independent from:
- exchange APIs
- Grid Engine
- Grid Backtest
- Grid Optimizer

It analyzes supplied market metrics and produces
a consistent crypto quality score.

Quality components
------------------
- Liquidity
- Volatility
- Trend stability
- Drawdown risk
- Recovery

The module does NOT decide whether to place a trade.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ============================================================
# RESULT
# ============================================================


@dataclass(frozen=True)
class CryptoQualityResult:
    """
    Result of crypto quality analysis.
    """

    symbol: str

    liquidity_score: float
    volatility_score: float
    trend_stability_score: float
    drawdown_risk_score: float
    recovery_score: float

    quality_score: float
    quality: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "liquidity_score": self.liquidity_score,
            "volatility_score": self.volatility_score,
            "trend_stability_score": self.trend_stability_score,
            "drawdown_risk_score": self.drawdown_risk_score,
            "recovery_score": self.recovery_score,
            "quality_score": self.quality_score,
            "quality": self.quality,
        }


# ============================================================
# ANALYZER
# ============================================================


class CryptoQualityAnalyzer:
    """
    Analyze crypto quality using five normalized scores.

    All component scores must be between 0 and 100.

    Overall quality score is calculated using weights:

        Liquidity        25%
        Volatility       20%
        Trend Stability  20%
        Drawdown Risk    20%
        Recovery         15%

    Total = 100%
    """

    LIQUIDITY_WEIGHT = 0.25
    VOLATILITY_WEIGHT = 0.20
    TREND_STABILITY_WEIGHT = 0.20
    DRAWDOWN_RISK_WEIGHT = 0.20
    RECOVERY_WEIGHT = 0.15

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """
        Normalize crypto symbol.

        Examples
        --------
        btcusdt
        BTC/USDT
        BTC-USDT
        BTC_USDT

        become:

        BTCUSDT
        """

        if not isinstance(symbol, str):
            raise TypeError(
                "symbol must be a string"
            )

        result = (
            symbol
            .strip()
            .upper()
            .replace("/", "")
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )

        if not result:
            raise ValueError(
                "symbol must not be empty"
            )

        return result

    @staticmethod
    def _validate_score(
        value: float,
        name: str,
    ) -> float:
        """
        Validate normalized score.

        Valid range:
            0 <= score <= 100
        """

        try:
            result = float(value)

        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{name} must be numeric"
            ) from exc

        if result < 0 or result > 100:
            raise ValueError(
                f"{name} must be between 0 and 100"
            )

        return result

    @staticmethod
    def classify_quality(
        quality_score: float,
    ) -> str:
        """
        Convert numeric quality score into a label.

        85 - 100 : EXCELLENT
        70 - 84  : GOOD
        55 - 69  : NEUTRAL
        40 - 54  : WEAK
         0 - 39  : AVOID
        """

        score = float(quality_score)

        if score >= 85:
            return "EXCELLENT"

        if score >= 70:
            return "GOOD"

        if score >= 55:
            return "NEUTRAL"

        if score >= 40:
            return "WEAK"

        return "AVOID"

    def analyze(
        self,
        symbol: str,
        liquidity_score: float,
        volatility_score: float,
        trend_stability_score: float,
        drawdown_risk_score: float,
        recovery_score: float,
    ) -> CryptoQualityResult:
        """
        Analyze one crypto asset.

        Parameters
        ----------
        symbol:
            Crypto trading symbol.

        liquidity_score:
            Score from 0 to 100.

        volatility_score:
            Score from 0 to 100.

        trend_stability_score:
            Score from 0 to 100.

        drawdown_risk_score:
            Higher score means lower drawdown risk.

        recovery_score:
            Score representing historical recovery quality.
        """

        normalized_symbol = self.normalize_symbol(
            symbol
        )

        liquidity = self._validate_score(
            liquidity_score,
            "liquidity_score",
        )

        volatility = self._validate_score(
            volatility_score,
            "volatility_score",
        )

        trend_stability = self._validate_score(
            trend_stability_score,
            "trend_stability_score",
        )

        drawdown_risk = self._validate_score(
            drawdown_risk_score,
            "drawdown_risk_score",
        )

        recovery = self._validate_score(
            recovery_score,
            "recovery_score",
        )

        quality_score = (
            liquidity
            * self.LIQUIDITY_WEIGHT

            + volatility
            * self.VOLATILITY_WEIGHT

            + trend_stability
            * self.TREND_STABILITY_WEIGHT

            + drawdown_risk
            * self.DRAWDOWN_RISK_WEIGHT

            + recovery
            * self.RECOVERY_WEIGHT
        )

        quality_score = round(
            quality_score,
            4,
        )

        quality = self.classify_quality(
            quality_score
        )

        return CryptoQualityResult(
            symbol=normalized_symbol,

            liquidity_score=liquidity,

            volatility_score=volatility,

            trend_stability_score=trend_stability,

            drawdown_risk_score=drawdown_risk,

            recovery_score=recovery,

            quality_score=quality_score,

            quality=quality,
        )

    def analyze_many(
        self,
        assets: list[dict[str, Any]],
    ) -> list[CryptoQualityResult]:
        """
        Analyze multiple crypto assets.

        Each item must contain:

            symbol
            liquidity_score
            volatility_score
            trend_stability_score
            drawdown_risk_score
            recovery_score
        """

        results = []

        for asset in assets:

            if not isinstance(
                asset,
                dict,
            ):
                raise TypeError(
                    "each asset must be a dictionary"
                )

            result = self.analyze(
                symbol=asset["symbol"],

                liquidity_score=(
                    asset["liquidity_score"]
                ),

                volatility_score=(
                    asset["volatility_score"]
                ),

                trend_stability_score=(
                    asset[
                        "trend_stability_score"
                    ]
                ),

                drawdown_risk_score=(
                    asset[
                        "drawdown_risk_score"
                    ]
                ),

                recovery_score=(
                    asset["recovery_score"]
                ),
            )

            results.append(
                result
            )

        return results

    def rank(
        self,
        assets: list[dict[str, Any]],
    ) -> list[CryptoQualityResult]:
        """
        Analyze and rank crypto assets.

        Highest quality score first.
        """

        results = self.analyze_many(
            assets
        )

        return sorted(
            results,
            key=lambda item: (
                item.quality_score,
                item.liquidity_score,
            ),
            reverse=True,
        )