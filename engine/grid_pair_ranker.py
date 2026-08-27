"""
==========================================
SULTAN QUANT OS
Module : Grid Pair Ranker
Version : 1.0.0
==========================================

Purpose
-------

Rank crypto pairs based on their suitability
for a SPOT Grid strategy.

The ranker combines multiple dimensions:

- Crypto quality
- Grid research metrics
- Market condition
- Historical recovery
- Drawdown risk
- Volatility suitability
- Grid profitability

This module is intentionally execution-independent.

It does NOT:

- Connect to exchanges
- Fetch live market data
- Place orders
- Manage API credentials

It only evaluates and ranks already available
market and research information.

Typical Flow
------------

Crypto Universe
        ↓
Crypto Quality Analyzer
        ↓
Grid Research / Backtest
        ↓
Grid Pair Ranker
        ↓
BEST / SUITABLE / CAUTION / AVOID
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable


# ============================================================
# Constants
# ============================================================

STATUS_BEST = "BEST"
STATUS_SUITABLE = "SUITABLE"
STATUS_CAUTION = "CAUTION"
STATUS_AVOID = "AVOID"

VALID_STATUSES = {
    STATUS_BEST,
    STATUS_SUITABLE,
    STATUS_CAUTION,
    STATUS_AVOID,
}


# ============================================================
# Helper Functions
# ============================================================

def _normalize_symbol(symbol: str) -> str:
    """
    Normalize crypto symbol.

    Examples
    --------
    btcusdt
    BTC/USDT
    BTC-USDT
    BTC_USDT

    becomes:

    BTCUSDT
    """

    if not isinstance(symbol, str):
        raise TypeError("symbol must be a string")

    normalized = (
        symbol.strip()
        .upper()
        .replace("/", "")
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
    )

    if not normalized:
        raise ValueError("symbol must not be empty")

    return normalized


def _clamp_score(value: Any) -> float:
    """
    Convert score to float and clamp between 0 and 100.
    """

    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(100.0, score))


def _normalize_ratio(value: Any) -> float:
    """
    Normalize ratio-like values.

    Accepts values between:

    0.0 -> 1.0

    Values outside the range are clamped.
    """

    try:
        ratio = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(1.0, ratio))


def _extract_first(data: dict[str, Any], keys: Iterable[str], default=None):
    """
    Return the first existing key from a dictionary.
    """

    for key in keys:
        if key in data:
            return data[key]

    return default


# ============================================================
# Result Model
# ============================================================

@dataclass(frozen=True)
class GridPairRankResult:
    """
    Final ranking result for one crypto pair.
    """

    symbol: str

    grid_score: float

    quality_score: float
    profitability_score: float
    recovery_score: float
    drawdown_score: float
    market_score: float
    volatility_score: float

    status: str

    rank: int | None = None

    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert result to dictionary.
        """

        result = asdict(self)

        if result["details"] is None:
            result["details"] = {}

        return result


# ============================================================
# Grid Pair Ranker
# ============================================================

class GridPairRanker:
    """
    Rank crypto pairs for Grid suitability.

    Score Composition
    -----------------

    quality_score:
        20%

    profitability_score:
        20%

    recovery_score:
        20%

    drawdown_score:
        15%

    market_score:
        15%

    volatility_score:
        10%

    Total:
        100%
    """

    QUALITY_WEIGHT = 0.20
    PROFITABILITY_WEIGHT = 0.20
    RECOVERY_WEIGHT = 0.20
    DRAWDOWN_WEIGHT = 0.15
    MARKET_WEIGHT = 0.15
    VOLATILITY_WEIGHT = 0.10

    def __init__(
        self,
        quality_weight: float = QUALITY_WEIGHT,
        profitability_weight: float = PROFITABILITY_WEIGHT,
        recovery_weight: float = RECOVERY_WEIGHT,
        drawdown_weight: float = DRAWDOWN_WEIGHT,
        market_weight: float = MARKET_WEIGHT,
        volatility_weight: float = VOLATILITY_WEIGHT,
    ):
        """
        Initialize Grid Pair Ranker.
        """

        weights = [
            quality_weight,
            profitability_weight,
            recovery_weight,
            drawdown_weight,
            market_weight,
            volatility_weight,
        ]

        if any(not isinstance(weight, (int, float)) for weight in weights):
            raise TypeError("all weights must be numeric")

        if any(float(weight) < 0 for weight in weights):
            raise ValueError("weights must not be negative")

        total_weight = sum(float(weight) for weight in weights)

        if total_weight <= 0:
            raise ValueError("total weight must be greater than zero")

        self.quality_weight = float(quality_weight) / total_weight
        self.profitability_weight = (
            float(profitability_weight) / total_weight
        )
        self.recovery_weight = float(recovery_weight) / total_weight
        self.drawdown_weight = float(drawdown_weight) / total_weight
        self.market_weight = float(market_weight) / total_weight
        self.volatility_weight = float(volatility_weight) / total_weight

    # ========================================================
    # Public API
    # ========================================================

    def analyze(
        self,
        symbol: str,
        quality: dict[str, Any] | None = None,
        research: dict[str, Any] | None = None,
        backtest: dict[str, Any] | None = None,
        market: dict[str, Any] | None = None,
    ) -> GridPairRankResult:
        """
        Analyze one crypto pair.

        Parameters
        ----------
        symbol:
            Crypto trading pair.

        quality:
            Result from Crypto Quality Analyzer.

        research:
            Result from Grid Research Engine.

        backtest:
            Result from Grid Backtest Engine.

        market:
            Market state information.

        Returns
        -------
        GridPairRankResult
        """

        normalized_symbol = _normalize_symbol(symbol)

        quality = quality if isinstance(quality, dict) else {}
        research = research if isinstance(research, dict) else {}
        backtest = backtest if isinstance(backtest, dict) else {}
        market = market if isinstance(market, dict) else {}

        quality_score = self._calculate_quality_score(quality)

        profitability_score = self._calculate_profitability_score(
            backtest
        )

        recovery_score = self._calculate_recovery_score(
            research
        )

        drawdown_score = self._calculate_drawdown_score(
            research,
            backtest,
        )

        market_score = self._calculate_market_score(
            market
        )

        volatility_score = self._calculate_volatility_score(
            market,
            research,
        )

        grid_score = (
            quality_score * self.quality_weight
            + profitability_score * self.profitability_weight
            + recovery_score * self.recovery_weight
            + drawdown_score * self.drawdown_weight
            + market_score * self.market_weight
            + volatility_score * self.volatility_weight
        )

        grid_score = round(_clamp_score(grid_score), 2)

        status = self._determine_status(grid_score)

        details = {
            "quality": dict(quality),
            "research": dict(research),
            "backtest": dict(backtest),
            "market": dict(market),
        }

        return GridPairRankResult(
            symbol=normalized_symbol,
            grid_score=grid_score,
            quality_score=round(quality_score, 2),
            profitability_score=round(profitability_score, 2),
            recovery_score=round(recovery_score, 2),
            drawdown_score=round(drawdown_score, 2),
            market_score=round(market_score, 2),
            volatility_score=round(volatility_score, 2),
            status=status,
            rank=None,
            details=details,
        )

    def rank(
        self,
        pairs: Iterable[dict[str, Any]],
    ) -> list[GridPairRankResult]:
        """
        Rank multiple crypto pairs.

        Each item may contain:

        {
            "symbol": "BTCUSDT",
            "quality": {...},
            "research": {...},
            "backtest": {...},
            "market": {...},
        }

        Returns results sorted from best to worst.
        """

        if pairs is None:
            return []

        if isinstance(pairs, (str, bytes)):
            raise TypeError("pairs must be an iterable of dictionaries")

        results: list[GridPairRankResult] = []

        for pair in pairs:

            if not isinstance(pair, dict):
                continue

            symbol = pair.get("symbol")

            if symbol is None:
                continue

            result = self.analyze(
                symbol=symbol,
                quality=pair.get("quality"),
                research=pair.get("research"),
                backtest=pair.get("backtest"),
                market=pair.get("market"),
            )

            results.append(result)

        results.sort(
            key=lambda item: item.grid_score,
            reverse=True,
        )

        ranked_results: list[GridPairRankResult] = []

        for index, result in enumerate(results, start=1):

            ranked_results.append(
                GridPairRankResult(
                    symbol=result.symbol,
                    grid_score=result.grid_score,
                    quality_score=result.quality_score,
                    profitability_score=result.profitability_score,
                    recovery_score=result.recovery_score,
                    drawdown_score=result.drawdown_score,
                    market_score=result.market_score,
                    volatility_score=result.volatility_score,
                    status=result.status,
                    rank=index,
                    details=result.details,
                )
            )

        return ranked_results

    def get_best(
        self,
        pairs: Iterable[dict[str, Any]],
        top_n: int = 5,
    ) -> list[GridPairRankResult]:
        """
        Return the best N Grid pairs.
        """

        if not isinstance(top_n, int):
            raise TypeError("top_n must be an integer")

        if top_n <= 0:
            raise ValueError("top_n must be greater than zero")

        ranked = self.rank(pairs)

        return ranked[:top_n]

    # ========================================================
    # Score Calculation
    # ========================================================

    def _calculate_quality_score(
        self,
        quality: dict[str, Any],
    ) -> float:
        """
        Calculate score from Crypto Quality Analyzer.
        """

        score = _extract_first(
            quality,
            [
                "quality_score",
                "score",
                "overall_score",
                "total_score",
            ],
            50.0,
        )

        return _clamp_score(score)

    def _calculate_profitability_score(
        self,
        backtest: dict[str, Any],
    ) -> float:
        """
        Convert Grid profitability into a 0-100 score.

        Priority:

        1. Explicit profitability_score
        2. net_profit_percent
        3. return_percent
        4. net_profit
        """

        explicit_score = _extract_first(
            backtest,
            [
                "profitability_score",
                "grid_profit_score",
            ],
        )

        if explicit_score is not None:
            return _clamp_score(explicit_score)

        profit_percent = _extract_first(
            backtest,
            [
                "net_profit_percent",
                "return_percent",
                "profit_percent",
                "roi_percent",
            ],
        )

        if profit_percent is not None:

            try:
                profit_percent = float(profit_percent)
            except (TypeError, ValueError):
                profit_percent = 0.0

            # 20% return or more = maximum score.
            return _clamp_score(
                (profit_percent / 20.0) * 100.0
            )

        net_profit = _extract_first(
            backtest,
            [
                "net_profit",
                "profit",
                "pnl",
            ],
            0.0,
        )

        try:
            net_profit = float(net_profit)
        except (TypeError, ValueError):
            net_profit = 0.0

        if net_profit <= 0:
            return 0.0

        return _clamp_score(net_profit)

    def _calculate_recovery_score(
        self,
        research: dict[str, Any],
    ) -> float:
        """
        Calculate recovery probability score.
        """

        value = _extract_first(
            research,
            [
                "recovery_probability",
                "probability_of_recovery",
                "conditional_recovery_probability",
                "recovery_rate",
            ],
            0.5,
        )

        ratio = _normalize_ratio(value)

        return ratio * 100.0

    def _calculate_drawdown_score(
        self,
        research: dict[str, Any],
        backtest: dict[str, Any],
    ) -> float:
        """
        Lower drawdown produces higher score.

        Priority:

        1. Explicit drawdown_score
        2. max_drawdown_percent
        3. max_drawdown
        """

        explicit_score = _extract_first(
            backtest,
            [
                "drawdown_score",
                "risk_score",
            ],
        )

        if explicit_score is not None:
            return _clamp_score(explicit_score)

        drawdown = _extract_first(
            backtest,
            [
                "max_drawdown_percent",
                "drawdown_percent",
            ],
        )

        if drawdown is None:

            drawdown = _extract_first(
                research,
                [
                    "max_drawdown_percent",
                    "drawdown_percent",
                    "maximum_drawdown",
                ],
                0.0,
            )

        try:
            drawdown = abs(float(drawdown))
        except (TypeError, ValueError):
            drawdown = 100.0

        # 0% drawdown = 100
        # 50% drawdown = 0
        score = 100.0 - ((drawdown / 50.0) * 100.0)

        return _clamp_score(score)

    def _calculate_market_score(
        self,
        market: dict[str, Any],
    ) -> float:
        """
        Score market condition for Grid.

        Grid generally prefers ranging or
        volatile-ranging conditions.
        """

        explicit_score = _extract_first(
            market,
            [
                "market_score",
                "grid_market_score",
            ],
        )

        if explicit_score is not None:
            return _clamp_score(explicit_score)

        regime = _extract_first(
            market,
            [
                "regime",
                "market_regime",
                "state",
            ],
            "",
        )

        if not isinstance(regime, str):
            return 50.0

        normalized = (
            regime.strip()
            .upper()
            .replace("-", "_")
            .replace(" ", "_")
        )

        regime_scores = {
            "RANGE": 100.0,
            "RANGING": 100.0,
            "SIDEWAYS": 95.0,
            "VOLATILE_RANGE": 90.0,
            "VOLATILE_RANGING": 90.0,
            "NEUTRAL": 65.0,
            "UNKNOWN": 50.0,
            "TREND": 40.0,
            "UPTREND": 35.0,
            "DOWNTREND": 25.0,
            "STRONG_TREND": 20.0,
            "STRONG_UPTREND": 25.0,
            "STRONG_DOWNTREND": 10.0,
            "HIGH_VOLATILITY": 55.0,
        }

        return regime_scores.get(
            normalized,
            50.0,
        )

    def _calculate_volatility_score(
        self,
        market: dict[str, Any],
        research: dict[str, Any],
    ) -> float:
        """
        Calculate volatility suitability for Grid.

        Grid generally benefits from moderate
        or moderately high volatility.

        Too little volatility:
            insufficient trading opportunities.

        Too much volatility:
            higher risk of exhausting layers.
        """

        explicit_score = _extract_first(
            market,
            [
                "volatility_score",
                "grid_volatility_score",
            ],
        )

        if explicit_score is not None:
            return _clamp_score(explicit_score)

        volatility = _extract_first(
            market,
            [
                "normalized_volatility",
                "volatility",
                "volatility_percent",
            ],
        )

        if volatility is None:

            volatility = _extract_first(
                research,
                [
                    "volatility",
                    "normalized_volatility",
                    "average_range_percent",
                ],
            )

        if volatility is None:
            return 50.0

        try:
            volatility = abs(float(volatility))
        except (TypeError, ValueError):
            return 50.0

        # If value appears to be a percentage,
        # normalize it.
        if volatility > 1.0:
            volatility = volatility / 100.0

        # Optimal approximate range:
        #
        # 1% -> 5% normalized movement
        #
        # Below 1%:
        # low opportunity
        #
        # Above 10%:
        # excessive risk

        if volatility < 0.01:
            return 30.0

        if volatility <= 0.05:
            return 100.0

        if volatility <= 0.10:
            return 75.0

        if volatility <= 0.20:
            return 50.0

        return 25.0

    # ========================================================
    # Classification
    # ========================================================

    def _determine_status(
        self,
        grid_score: float,
    ) -> str:
        """
        Determine Grid suitability status.
        """

        if grid_score >= 80.0:
            return STATUS_BEST

        if grid_score >= 65.0:
            return STATUS_SUITABLE

        if grid_score >= 45.0:
            return STATUS_CAUTION

        return STATUS_AVOID


# ============================================================
# Convenience Function
# ============================================================

def rank_grid_pairs(
    pairs: Iterable[dict[str, Any]],
    **kwargs,
) -> list[GridPairRankResult]:
    """
    Convenience function.

    Example
    -------

    results = rank_grid_pairs(
        pairs
    )
    """

    ranker = GridPairRanker(
        **kwargs
    )

    return ranker.rank(
        pairs
    )