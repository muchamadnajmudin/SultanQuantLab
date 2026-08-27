import pytest

from engine.crypto_quality import (
    CryptoQualityAnalyzer,
    CryptoQualityResult,
)


# ============================================================
# BASIC ANALYSIS
# ============================================================


def test_analyze_crypto():

    analyzer = CryptoQualityAnalyzer()

    result = analyzer.analyze(
        symbol="BTCUSDT",
        liquidity_score=95,
        volatility_score=85,
        trend_stability_score=90,
        drawdown_risk_score=80,
        recovery_score=88,
    )

    assert isinstance(
        result,
        CryptoQualityResult,
    )

    assert result.symbol == "BTCUSDT"

    assert result.quality_score > 0

    assert result.quality == "EXCELLENT"


# ============================================================
# SYMBOL NORMALIZATION
# ============================================================


def test_symbol_normalization():

    analyzer = CryptoQualityAnalyzer()

    assert (
        analyzer.normalize_symbol(
            "btcusdt"
        )
        == "BTCUSDT"
    )

    assert (
        analyzer.normalize_symbol(
            "BTC/USDT"
        )
        == "BTCUSDT"
    )

    assert (
        analyzer.normalize_symbol(
            "BTC-USDT"
        )
        == "BTCUSDT"
    )

    assert (
        analyzer.normalize_symbol(
            "BTC_USDT"
        )
        == "BTCUSDT"
    )


# ============================================================
# WEIGHT CALCULATION
# ============================================================


def test_quality_score_calculation():

    analyzer = CryptoQualityAnalyzer()

    result = analyzer.analyze(
        symbol="TESTUSDT",
        liquidity_score=100,
        volatility_score=100,
        trend_stability_score=100,
        drawdown_risk_score=100,
        recovery_score=100,
    )

    assert result.quality_score == 100.0

    assert result.quality == "EXCELLENT"


def test_weighted_score():

    analyzer = CryptoQualityAnalyzer()

    result = analyzer.analyze(
        symbol="TESTUSDT",
        liquidity_score=80,
        volatility_score=80,
        trend_stability_score=80,
        drawdown_risk_score=80,
        recovery_score=80,
    )

    assert result.quality_score == 80.0

    assert result.quality == "GOOD"


# ============================================================
# QUALITY CLASSIFICATION
# ============================================================


def test_excellent_quality():

    analyzer = CryptoQualityAnalyzer()

    assert (
        analyzer.classify_quality(90)
        == "EXCELLENT"
    )


def test_good_quality():

    analyzer = CryptoQualityAnalyzer()

    assert (
        analyzer.classify_quality(75)
        == "GOOD"
    )


def test_neutral_quality():

    analyzer = CryptoQualityAnalyzer()

    assert (
        analyzer.classify_quality(60)
        == "NEUTRAL"
    )


def test_weak_quality():

    analyzer = CryptoQualityAnalyzer()

    assert (
        analyzer.classify_quality(45)
        == "WEAK"
    )


def test_avoid_quality():

    analyzer = CryptoQualityAnalyzer()

    assert (
        analyzer.classify_quality(20)
        == "AVOID"
    )


# ============================================================
# RESULT SERIALIZATION
# ============================================================


def test_result_to_dict():

    analyzer = CryptoQualityAnalyzer()

    result = analyzer.analyze(
        symbol="ETHUSDT",
        liquidity_score=90,
        volatility_score=80,
        trend_stability_score=85,
        drawdown_risk_score=75,
        recovery_score=80,
    )

    data = result.to_dict()

    assert isinstance(
        data,
        dict,
    )

    assert data["symbol"] == "ETHUSDT"

    assert (
        "quality_score"
        in data
    )

    assert (
        "quality"
        in data
    )


# ============================================================
# MULTIPLE ASSETS
# ============================================================


def test_analyze_many():

    analyzer = CryptoQualityAnalyzer()

    assets = [

        {
            "symbol": "BTCUSDT",
            "liquidity_score": 95,
            "volatility_score": 85,
            "trend_stability_score": 90,
            "drawdown_risk_score": 80,
            "recovery_score": 88,
        },

        {
            "symbol": "TESTUSDT",
            "liquidity_score": 50,
            "volatility_score": 50,
            "trend_stability_score": 50,
            "drawdown_risk_score": 50,
            "recovery_score": 50,
        },

    ]

    results = analyzer.analyze_many(
        assets
    )

    assert len(results) == 2

    assert results[0].symbol == "BTCUSDT"

    assert results[1].symbol == "TESTUSDT"


# ============================================================
# RANKING
# ============================================================


def test_rank_assets():

    analyzer = CryptoQualityAnalyzer()

    assets = [

        {
            "symbol": "WEAKUSDT",
            "liquidity_score": 40,
            "volatility_score": 40,
            "trend_stability_score": 40,
            "drawdown_risk_score": 40,
            "recovery_score": 40,
        },

        {
            "symbol": "STRONGUSDT",
            "liquidity_score": 90,
            "volatility_score": 90,
            "trend_stability_score": 90,
            "drawdown_risk_score": 90,
            "recovery_score": 90,
        },

    ]

    results = analyzer.rank(
        assets
    )

    assert len(results) == 2

    assert (
        results[0].symbol
        == "STRONGUSDT"
    )

    assert (
        results[1].symbol
        == "WEAKUSDT"
    )


# ============================================================
# INVALID SYMBOL
# ============================================================


def test_invalid_empty_symbol():

    analyzer = CryptoQualityAnalyzer()

    with pytest.raises(
        ValueError
    ):

        analyzer.normalize_symbol(
            ""
        )


def test_invalid_symbol_type():

    analyzer = CryptoQualityAnalyzer()

    with pytest.raises(
        TypeError
    ):

        analyzer.normalize_symbol(
            None
        )


# ============================================================
# INVALID SCORES
# ============================================================


def test_negative_score():

    analyzer = CryptoQualityAnalyzer()

    with pytest.raises(
        ValueError
    ):

        analyzer.analyze(
            symbol="BTCUSDT",
            liquidity_score=-1,
            volatility_score=50,
            trend_stability_score=50,
            drawdown_risk_score=50,
            recovery_score=50,
        )


def test_score_above_100():

    analyzer = CryptoQualityAnalyzer()

    with pytest.raises(
        ValueError
    ):

        analyzer.analyze(
            symbol="BTCUSDT",
            liquidity_score=101,
            volatility_score=50,
            trend_stability_score=50,
            drawdown_risk_score=50,
            recovery_score=50,
        )


def test_invalid_score_type():

    analyzer = CryptoQualityAnalyzer()

    with pytest.raises(
        TypeError
    ):

        analyzer.analyze(
            symbol="BTCUSDT",
            liquidity_score="invalid",
            volatility_score=50,
            trend_stability_score=50,
            drawdown_risk_score=50,
            recovery_score=50,
        )


# ============================================================
# INVALID ASSET COLLECTION
# ============================================================


def test_invalid_asset_collection():

    analyzer = CryptoQualityAnalyzer()

    with pytest.raises(
        TypeError
    ):

        analyzer.analyze_many(
            [
                "BTCUSDT",
            ]
        )