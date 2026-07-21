"""
==========================================
SULTAN QUANT OS
Optimizer Runner
Version : 2.1
==========================================
"""

from engine.optimizer_engine import optimize


PARAMETER_GRID = {

    "RSI_OVERSOLD": [
        5,
        10,
        15,
    ],

    "RSI_OVERBOUGHT": [
        85,
        90,
        95,
    ],

}


def main():

    print("=" * 50)
    print("SULTAN QUANT OS OPTIMIZER")
    print("=" * 50)

    results = optimize(
        data_file="data/XAUUSDc_M1.csv",
        parameter_grid=PARAMETER_GRID,
    )

    if not results:

        print("Tidak ada hasil.")

        return

    print()

    print("=" * 50)
    print("BEST RESULT")
    print("=" * 50)

    print(results[0])


if __name__ == "__main__":

    main()