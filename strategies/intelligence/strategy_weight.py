"""
==========================================

SULTAN QUANT OS

Strategy Weight Engine

==========================================

"""


def calculate_weight(
performance
):


    score = 0


    score += performance.get(

        "win_rate",

        0

    )


    score += performance.get(

        "profit",

        0

    )


    return score



def normalize_weights(scores):


    total = sum(

        scores.values()

    )


    if total == 0:


        return {

            k:0

            for k in scores

        }



    return {


        k:

        round(

            v / total,

            2

        )


        for k,v in scores.items()

    }