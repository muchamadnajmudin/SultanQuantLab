from strategies.intelligence.strategy_memory import (
    StrategyMemory,
)

from strategies.intelligence.strategy_weight import (
    calculate_weight,
    normalize_weights,
    build_weights,
)

from strategies.intelligence.adaptive_selector import (
    select_best_strategy,
)


# ==================================================
# MEMORY
# ==================================================

def test_memory_tracks_wins_losses():

    memory = StrategyMemory()

    memory.update(
        strategy="price_action",
        regime="TRENDING",
        profit=100,
        win=True,
    )

    memory.update(
        strategy="price_action",
        regime="TRENDING",
        profit=-50,
        win=False,
    )

    result = memory.get(
        "price_action",
        "TRENDING",
    )

    assert result["trades"] == 2

    assert result["wins"] == 1

    assert result["losses"] == 1

    assert result["profit"] == 50

    assert result["win_rate"] == 50


# ==================================================
# MEMORY REGIME
# ==================================================

def test_memory_separates_regimes():

    memory = StrategyMemory()

    memory.update(
        "breakout",
        "TRENDING",
        100,
        True,
    )

    memory.update(
        "breakout",
        "RANGE",
        -20,
        False,
    )

    trending = memory.get(
        "breakout",
        "TRENDING",
    )

    ranging = memory.get(
        "breakout",
        "RANGE",
    )

    assert trending["profit"] == 100

    assert ranging["profit"] == -20


# ==================================================
# WEIGHT
# ==================================================

def test_weight_advanced_metrics():

    score = calculate_weight({

        "win_rate": 60,

        "profit": 50,

        "profit_factor": 2.0,

        "expectancy": 1.5,

        "trades": 100,

    })

    assert score > 0


# ==================================================
# NORMALIZATION
# ==================================================

def test_normalize_weights():

    weights = normalize_weights({

        "price_action": 60,

        "breakout": 40,

    })

    assert weights["price_action"] == 0.6

    assert weights["breakout"] == 0.4

    assert sum(
        weights.values()
    ) == 1.0


# ==================================================
# BUILD WEIGHTS
# ==================================================

def test_build_weights():

    weights = build_weights({

        "price_action": {

            "win_rate": 60,

            "profit": 100,

            "profit_factor": 2,

            "expectancy": 1,

            "trades": 100,

        },

        "breakout": {

            "win_rate": 50,

            "profit": 50,

            "profit_factor": 1.5,

            "expectancy": 0.5,

            "trades": 100,

        },

    })

    assert weights

    assert (
        abs(
            sum(weights.values())
            -
            1.0
        )
        < 0.001
    )


# ==================================================
# ADAPTIVE SELECTOR
# ==================================================

def test_adaptive_selector():

    strategy = select_best_strategy({

        "price_action": 0.40,

        "breakout": 0.60,

    })

    assert strategy == "breakout"


# ==================================================
# CANDIDATE RESTRICTION
# ==================================================

def test_adaptive_selector_candidates():

    strategy = select_best_strategy(

        {

            "price_action": 0.40,

            "breakout": 0.60,

            "fibonacci": 0.80,

        },

        candidates=[

            "price_action",

            "breakout",

        ],

    )

    assert strategy == "breakout"