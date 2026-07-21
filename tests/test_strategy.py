from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy

df = load_data("data/XAUUSDc_M1.csv")

df = calculate_indicators(df)

df = run_strategy(df)

print("=" * 50)
print("SULTAN QUANT LAB")
print("Strategy Test")
print("=" * 50)

print()

print("BUY SIGNAL :", int(df["BUY"].sum()))
print("SELL SIGNAL:", int(df["SELL"].sum()))

print()

print(df[
    [
        "time",
        "close",
        "BUY",
        "SELL"
    ]
].tail(20))