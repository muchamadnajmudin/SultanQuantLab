"""
==========================================
SULTAN QUANT OS
Strategy Memory Engine
Version : 2.0.0
==========================================

Responsibilities:

- Store strategy performance
- Store performance by market regime
- Track trades
- Track wins / losses
- Track cumulative profit
- Calculate historical win rate
- Calculate average profit
- Retrieve strategy history
- Preserve backward compatibility
==========================================
"""


# ==================================================
# DEFAULT RECORD
# ==================================================

def _empty_record():

    return {

        "trades": 0,

        "wins": 0,

        "losses": 0,

        "profit": 0.0,

        "win_rate": 0.0,

        "average_profit": 0.0,

    }


# ==================================================
# STRATEGY MEMORY
# ==================================================

class StrategyMemory:

    def __init__(self):

        self.memory = {}


    # ==================================================
    # SAVE RESULT
    # ==================================================

    def update(
        self,
        strategy,
        regime,
        profit,
        win,
    ):

        key = (
            regime,
            strategy,
        )

        if key not in self.memory:

            self.memory[key] = _empty_record()

        record = self.memory[key]

        profit = float(profit or 0)

        record["trades"] += 1

        if win:

            record["wins"] += 1

        else:

            record["losses"] += 1

        record["profit"] += profit

        record["win_rate"] = (

            record["wins"]
            /
            record["trades"]
            *
            100

        )

        record["average_profit"] = (

            record["profit"]
            /
            record["trades"]

        )

    # ==================================================
    # GET
    # ==================================================

    def get(
        self,
        strategy,
        regime,
    ):

        key = (
            regime,
            strategy,
        )

        if key not in self.memory:

            return _empty_record()

        return self.memory[key].copy()

    # ==================================================
    # GET STRATEGY HISTORY
    # ==================================================

    def get_strategy_history(
        self,
        strategy,
    ):

        history = {}

        for (
            regime,
            stored_strategy,
        ), record in self.memory.items():

            if stored_strategy != strategy:

                continue

            history[regime] = record.copy()

        return history

    # ==================================================
    # GET REGIME HISTORY
    # ==================================================

    def get_regime_history(
        self,
        regime,
    ):

        history = {}

        for (
            stored_regime,
            strategy,
        ), record in self.memory.items():

            if stored_regime != regime:

                continue

            history[strategy] = record.copy()

        return history

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self):

        return {

            key: value.copy()

            for key, value
            in self.memory.items()

        }


# ==================================================
# GLOBAL MEMORY
# ==================================================

_memory = StrategyMemory()


# ==================================================
# UPDATE MEMORY
# ==================================================

def update_memory(
    strategy,
    statistics,
    regime="UNKNOWN",
):

    if not isinstance(
        statistics,
        dict,
    ):

        return

    # --------------------------------------------------
    # IMPORTANT
    #
    # A backtest result represents MANY trades.
    #
    # We therefore store the aggregate result as one
    # historical observation while calculating wins from
    # win_rate and trade count.
    # --------------------------------------------------

    profit = statistics.get(
        "net_profit",
        0,
    )

    win_rate = statistics.get(
        "win_rate",
        0,
    )

    total_trades = (

        statistics.get(
            "total_trade",
            statistics.get(
                "total_trades",
                0,
            ),
        )

    )

    try:

        total_trades = max(
            0,
            int(float(total_trades)),
        )

    except (
        TypeError,
        ValueError,
    ):

        total_trades = 0

    # --------------------------------------------------
    # Backward-compatible aggregate observation
    #
    # If total trade information exists, preserve the
    # actual number of trades.
    # --------------------------------------------------

    if total_trades > 0:

        wins = round(

            total_trades
            *
            float(win_rate or 0)
            /
            100

        )

        losses = max(
            0,
            total_trades - wins,
        )

        key = (
            regime,
            strategy,
        )

        if key not in _memory.memory:

            _memory.memory[key] = _empty_record()

        record = _memory.memory[key]

        record["trades"] += total_trades

        record["wins"] += wins

        record["losses"] += losses

        record["profit"] += float(
            profit or 0
        )

        if record["trades"] > 0:

            record["win_rate"] = (

                record["wins"]
                /
                record["trades"]
                *
                100

            )

            record["average_profit"] = (

                record["profit"]
                /
                record["trades"]

            )

        return

    # --------------------------------------------------
    # Legacy fallback
    # --------------------------------------------------

    _memory.update(

        strategy=strategy,

        regime=regime,

        profit=profit,

        win=(
            float(win_rate or 0)
            >= 50
        ),

    )


# ==================================================
# GET MEMORY
# ==================================================

def get_memory(
    strategy,
    regime="UNKNOWN",
):

    return _memory.get(
        strategy,
        regime,
    )


# ==================================================
# GET STRATEGY HISTORY
# ==================================================

def get_strategy_history(
    strategy,
):

    return _memory.get_strategy_history(
        strategy,
    )


# ==================================================
# GET REGIME HISTORY
# ==================================================

def get_regime_history(
    regime,
):

    return _memory.get_regime_history(
        regime,
    )


# ==================================================
# MEMORY SUMMARY
# ==================================================

def memory_summary():

    return _memory.summary()