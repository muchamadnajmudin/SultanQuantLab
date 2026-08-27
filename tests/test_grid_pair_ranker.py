import pytest

from engine.grid_pair_ranker import (
    GridPairRanker,
    GridPairRankResult,
    STATUS_AVOID,
    STATUS_BEST,
    STATUS_CAUTION,
    STATUS_SUITABLE,
    rank_grid_pairs,
)


# ============================================================
# Basic Creation
# ============================================================

def test_ranker_creation():
    ranker = GridPairRanker()

    assert isinstance(ranker, GridPairRanker)


def test_default_weights_sum_to_one():
    ranker = GridPairRanker()

    total = (
        ranker.quality_weight
        + ranker.profitability_weight
        + ranker.recovery_weight
        + ranker.drawdown_weight
        + ranker.market_weight
        + ranker.volatility_weight
    )

    assert total == pytest.approx(1.0)


# ============================================================
# Symbol Normalization
# ============================================================

@pytest.mark.parametrize(
    "symbol,expected",
    [
        ("btcusdt", "BTCUSDT"),
        ("BTC/USDT", "BTCUSDT"),
        ("BTC-USDT", "BTCUSDT"),
        ("BTC_USDT", "BTCUSDT"),
        (" btcusdt ", "BTCUSDT"),
    ],
)
def test_symbol_normalization(symbol, expected):
    ranker = GridPairRanker()

    result = ranker.analyze(symbol)

    assert result.symbol == expected


def test_invalid_empty_symbol():
    ranker = GridPairRanker()

    with pytest.raises(ValueError):
        ranker.analyze("")


def test_invalid_symbol_type():
    ranker = GridPairRanker()

    with pytest.raises(TypeError):
        ranker.analyze(None)


# ============================================================
# Result Contract
# ============================================================

def test_analyze_returns_result():
    ranker = GridPairRanker()

    result = ranker.analyze("BTCUSDT")

    assert isinstance(result, GridPairRankResult)


def test_result_has_required_values():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality={"quality_score": 80},
        research={"recovery_probability": 0.80},
        backtest={
            "net_profit_percent": 10,
            "max_drawdown_percent": 10,
        },
        market={
            "regime": "RANGE",
            "volatility": 0.03,
        },
    )

    assert result.symbol == "BTCUSDT"

    assert 0 <= result.grid_score <= 100
    assert 0 <= result.quality_score <= 100
    assert 0 <= result.profitability_score <= 100
    assert 0 <= result.recovery_score <= 100
    assert 0 <= result.drawdown_score <= 100
    assert 0 <= result.market_score <= 100
    assert 0 <= result.volatility_score <= 100


def test_result_to_dict():
    ranker = GridPairRanker()

    result = ranker.analyze("BTCUSDT")

    data = result.to_dict()

    assert isinstance(data, dict)

    assert data["symbol"] == "BTCUSDT"

    assert "grid_score" in data
    assert "quality_score" in data
    assert "profitability_score" in data
    assert "recovery_score" in data
    assert "drawdown_score" in data
    assert "market_score" in data
    assert "volatility_score" in data
    assert "status" in data
    assert "rank" in data
    assert "details" in data


# ============================================================
# Quality Score
# ============================================================

def test_quality_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality={
            "quality_score": 85,
        },
    )

    assert result.quality_score == 85


def test_quality_score_alternative_key():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality={
            "overall_score": 90,
        },
    )

    assert result.quality_score == 90


def test_quality_score_is_clamped():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality={
            "quality_score": 150,
        },
    )

    assert result.quality_score == 100


# ============================================================
# Profitability Score
# ============================================================

def test_profitability_score_from_explicit_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        backtest={
            "profitability_score": 88,
        },
    )

    assert result.profitability_score == 88


def test_profitability_score_from_return():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        backtest={
            "net_profit_percent": 10,
        },
    )

    # 10% / 20% * 100 = 50
    assert result.profitability_score == 50


def test_profitability_score_maximum():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        backtest={
            "net_profit_percent": 20,
        },
    )

    assert result.profitability_score == 100


def test_negative_profitability_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        backtest={
            "net_profit_percent": -10,
        },
    )

    assert result.profitability_score == 0


# ============================================================
# Recovery Score
# ============================================================

def test_recovery_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        research={
            "recovery_probability": 0.80,
        },
    )

    assert result.recovery_score == 80


def test_recovery_score_alternative_key():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        research={
            "recovery_rate": 0.75,
        },
    )

    assert result.recovery_score == 75


def test_recovery_score_is_clamped():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        research={
            "recovery_probability": 2.0,
        },
    )

    assert result.recovery_score == 100


# ============================================================
# Drawdown Score
# ============================================================

def test_drawdown_score_low_drawdown():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        backtest={
            "max_drawdown_percent": 10,
        },
    )

    # 100 - (10 / 50 * 100) = 80
    assert result.drawdown_score == 80


def test_drawdown_score_high_drawdown():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        backtest={
            "max_drawdown_percent": 50,
        },
    )

    assert result.drawdown_score == 0


def test_drawdown_score_explicit():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        backtest={
            "drawdown_score": 77,
        },
    )

    assert result.drawdown_score == 77


# ============================================================
# Market Score
# ============================================================

@pytest.mark.parametrize(
    "regime,expected",
    [
        ("RANGE", 100),
        ("RANGING", 100),
        ("SIDEWAYS", 95),
        ("VOLATILE_RANGE", 90),
        ("NEUTRAL", 65),
        ("TREND", 40),
        ("UPTREND", 35),
        ("DOWNTREND", 25),
        ("STRONG_TREND", 20),
        ("STRONG_DOWNTREND", 10),
    ],
)
def test_market_regime_scores(regime, expected):
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        market={
            "regime": regime,
        },
    )

    assert result.market_score == expected


def test_explicit_market_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        market={
            "market_score": 83,
        },
    )

    assert result.market_score == 83


# ============================================================
# Volatility Score
# ============================================================

def test_optimal_volatility_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        market={
            "volatility": 0.03,
        },
    )

    assert result.volatility_score == 100


def test_low_volatility_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        market={
            "volatility": 0.005,
        },
    )

    assert result.volatility_score == 30


def test_high_volatility_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        market={
            "volatility": 0.15,
        },
    )

    assert result.volatility_score == 50


def test_extreme_volatility_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        market={
            "volatility": 0.50,
        },
    )

    assert result.volatility_score == 25


def test_explicit_volatility_score():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        market={
            "volatility_score": 92,
        },
    )

    assert result.volatility_score == 92


# ============================================================
# Status Classification
# ============================================================

def test_best_status():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality={"quality_score": 100},
        research={
            "recovery_probability": 1.0,
        },
        backtest={
            "profitability_score": 100,
            "drawdown_score": 100,
        },
        market={
            "market_score": 100,
            "volatility_score": 100,
        },
    )

    assert result.grid_score == 100
    assert result.status == STATUS_BEST


def test_suitable_status():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality={"quality_score": 70},
        research={
            "recovery_probability": 0.70,
        },
        backtest={
            "profitability_score": 70,
            "drawdown_score": 70,
        },
        market={
            "market_score": 70,
            "volatility_score": 70,
        },
    )

    assert result.status == STATUS_SUITABLE


def test_caution_status():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality={"quality_score": 50},
        research={
            "recovery_probability": 0.50,
        },
        backtest={
            "profitability_score": 50,
            "drawdown_score": 50,
        },
        market={
            "market_score": 50,
            "volatility_score": 50,
        },
    )

    assert result.status == STATUS_CAUTION


def test_avoid_status():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality={"quality_score": 20},
        research={
            "recovery_probability": 0.20,
        },
        backtest={
            "profitability_score": 20,
            "drawdown_score": 20,
        },
        market={
            "market_score": 20,
            "volatility_score": 20,
        },
    )

    assert result.status == STATUS_AVOID


# ============================================================
# Ranking
# ============================================================

def test_rank_multiple_pairs():
    ranker = GridPairRanker()

    pairs = [
        {
            "symbol": "WEAKUSDT",
            "quality": {
                "quality_score": 20,
            },
            "research": {
                "recovery_probability": 0.20,
            },
            "backtest": {
                "profitability_score": 20,
                "drawdown_score": 20,
            },
            "market": {
                "market_score": 20,
                "volatility_score": 20,
            },
        },
        {
            "symbol": "BESTUSDT",
            "quality": {
                "quality_score": 95,
            },
            "research": {
                "recovery_probability": 0.95,
            },
            "backtest": {
                "profitability_score": 95,
                "drawdown_score": 95,
            },
            "market": {
                "market_score": 95,
                "volatility_score": 95,
            },
        },
        {
            "symbol": "MIDUSDT",
            "quality": {
                "quality_score": 60,
            },
            "research": {
                "recovery_probability": 0.60,
            },
            "backtest": {
                "profitability_score": 60,
                "drawdown_score": 60,
            },
            "market": {
                "market_score": 60,
                "volatility_score": 60,
            },
        },
    ]

    results = ranker.rank(pairs)

    assert len(results) == 3

    assert results[0].symbol == "BESTUSDT"
    assert results[1].symbol == "MIDUSDT"
    assert results[2].symbol == "WEAKUSDT"

    assert results[0].rank == 1
    assert results[1].rank == 2
    assert results[2].rank == 3


def test_rank_empty():
    ranker = GridPairRanker()

    results = ranker.rank([])

    assert results == []


def test_rank_none():
    ranker = GridPairRanker()

    results = ranker.rank(None)

    assert results == []


def test_rank_skips_invalid_items():
    ranker = GridPairRanker()

    pairs = [
        None,
        "BTCUSDT",
        {},
        {
            "symbol": "BTCUSDT",
            "quality": {
                "quality_score": 80,
            },
        },
    ]

    results = ranker.rank(pairs)

    assert len(results) == 1
    assert results[0].symbol == "BTCUSDT"


def test_rank_invalid_string_input():
    ranker = GridPairRanker()

    with pytest.raises(TypeError):
        ranker.rank("BTCUSDT")


# ============================================================
# Best Pairs
# ============================================================

def test_get_best():
    ranker = GridPairRanker()

    pairs = [
        {
            "symbol": "AUSDT",
            "quality": {
                "quality_score": 40,
            },
        },
        {
            "symbol": "BUSDT",
            "quality": {
                "quality_score": 90,
            },
        },
        {
            "symbol": "CUSDT",
            "quality": {
                "quality_score": 70,
            },
        },
    ]

    results = ranker.get_best(
        pairs,
        top_n=2,
    )

    assert len(results) == 2

    assert results[0].symbol == "BUSDT"
    assert results[1].symbol == "CUSDT"


def test_get_best_invalid_top_n():
    ranker = GridPairRanker()

    with pytest.raises(ValueError):
        ranker.get_best([], top_n=0)


def test_get_best_invalid_top_n_type():
    ranker = GridPairRanker()

    with pytest.raises(TypeError):
        ranker.get_best([], top_n="2")


# ============================================================
# Custom Weights
# ============================================================

def test_custom_weights_are_normalized():
    ranker = GridPairRanker(
        quality_weight=2,
        profitability_weight=2,
        recovery_weight=2,
        drawdown_weight=2,
        market_weight=1,
        volatility_weight=1,
    )

    total = (
        ranker.quality_weight
        + ranker.profitability_weight
        + ranker.recovery_weight
        + ranker.drawdown_weight
        + ranker.market_weight
        + ranker.volatility_weight
    )

    assert total == pytest.approx(1.0)


def test_invalid_negative_weight():
    with pytest.raises(ValueError):
        GridPairRanker(
            quality_weight=-1,
        )


def test_invalid_weight_type():
    with pytest.raises(TypeError):
        GridPairRanker(
            quality_weight="invalid",
        )


def test_zero_total_weight():
    with pytest.raises(ValueError):
        GridPairRanker(
            quality_weight=0,
            profitability_weight=0,
            recovery_weight=0,
            drawdown_weight=0,
            market_weight=0,
            volatility_weight=0,
        )


# ============================================================
# Convenience Function
# ============================================================

def test_rank_grid_pairs_function():
    pairs = [
        {
            "symbol": "BTCUSDT",
            "quality": {
                "quality_score": 90,
            },
        },
        {
            "symbol": "WEAKUSDT",
            "quality": {
                "quality_score": 20,
            },
        },
    ]

    results = rank_grid_pairs(pairs)

    assert isinstance(results, list)

    assert len(results) == 2

    assert results[0].symbol == "BTCUSDT"
    assert results[1].symbol == "WEAKUSDT"


# ============================================================
# Input Safety
# ============================================================

def test_non_dict_inputs_are_safe():
    ranker = GridPairRanker()

    result = ranker.analyze(
        "BTCUSDT",
        quality="invalid",
        research=[],
        backtest=None,
        market=123,
    )

    assert isinstance(result, GridPairRankResult)

    assert 0 <= result.grid_score <= 100


def test_details_are_preserved():
    ranker = GridPairRanker()

    quality = {
        "quality_score": 85,
    }

    research = {
        "recovery_probability": 0.80,
    }

    backtest = {
        "net_profit_percent": 12,
    }

    market = {
        "regime": "RANGE",
    }

    result = ranker.analyze(
        "BTCUSDT",
        quality=quality,
        research=research,
        backtest=backtest,
        market=market,
    )

    assert result.details["quality"] == quality
    assert result.details["research"] == research
    assert result.details["backtest"] == backtest
    assert result.details["market"] == market