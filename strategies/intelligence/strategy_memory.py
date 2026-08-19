"""
==========================================

SULTAN QUANT OS

Strategy Memory Engine

Version : 1.0.0

==========================================

Responsibilities:

- Store strategy performance
- Retrieve history

"""


class StrategyMemory:


    def __init__(self):

        self.memory = {}



    # ======================================
    # SAVE RESULT
    # ======================================

    def update(
        self,
        strategy,
        regime,
        profit,
        win
    ):


        key = (

            regime,

            strategy,

        )


        if key not in self.memory:


            self.memory[key] = {

                "trades":0,

                "wins":0,

                "profit":0,

            }


        self.memory[key]["trades"] += 1


        if win:

            self.memory[key]["wins"] += 1


        self.memory[key]["profit"] += profit



    # ======================================
    # GET
    # ======================================

    def get(
        self,
        strategy,
        regime
    ):


        return self.memory.get(

            (
                regime,
                strategy
            ),

            {

                "trades":0,

                "wins":0,

                "profit":0,

            }

        )



    # ======================================
    # SUMMARY
    # ======================================

    def summary(self):

        return self.memory

# ==================================================
# GLOBAL MEMORY
# ==================================================

_memory = StrategyMemory()


# ==================================================
# UPDATE MEMORY
# ==================================================

def update_memory(strategy, statistics, regime="UNKNOWN"):

    profit = statistics.get(
        "net_profit",
        0,
    )

    win_rate = statistics.get(
        "win_rate",
        0,
    )

    _memory.update(

        strategy=strategy,

        regime=regime,

        profit=profit,

        win=(win_rate >= 50),

    )


# ==================================================
# GET MEMORY
# ==================================================

def get_memory(strategy, regime="UNKNOWN"):

    return _memory.get(

        strategy,

        regime,

    )


# ==================================================
# MEMORY SUMMARY
# ==================================================

def memory_summary():

    return _memory.summary()        