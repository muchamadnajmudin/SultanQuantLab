"""
==========================================

SULTAN QUANT OS

Adaptive Strategy Selector

==========================================

"""


def select_best_strategy(
weights
):


    if not weights:

        return None



    return max(

        weights,

        key=weights.get

    )