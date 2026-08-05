"""
==========================================
SULTAN QUANT OS
Test Strategy Manager
Version : 1.0.0
==========================================
"""

from engine.loader import load_data
from engine.indicator_engine import calculate_indicators

from strategies.strategy_manager import (
    StrategyManager,
)


DATA_FILE = "data/XAUUSDc_M1.csv"


# ==================================================
# TEST AVAILABLE
# ==================================================

def test_strategy_manager_available():

    manager = StrategyManager()

    strategies = manager.available()

    assert isinstance(strategies, list)

    assert "xau_strategy" in strategies


# ==================================================
# TEST BEST STRATEGY
# ==================================================

def test_strategy_manager_best():

    df = load_data(DATA_FILE)

    df = calculate_indicators(df)

    manager = StrategyManager()

    result = manager.best(df)

    assert result is not None

    assert isinstance(result, dict)

    assert "name" in result

    assert "score" in result

    assert "grade" in result