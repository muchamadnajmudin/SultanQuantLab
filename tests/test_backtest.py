from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy
from engine.backtest_engine import run_backtest

df = load_data("data/XAUUSDc_M1.csv")

df = calculate_indicators(df)

df = run_strategy(df)

trades = run_backtest(df)

print("Jumlah Trade :", len(trades))

if trades:
    print(trades[0])