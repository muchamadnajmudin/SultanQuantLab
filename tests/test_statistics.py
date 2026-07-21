from engine.trade import Trade
from engine.statistics_engine import calculate_statistics

trades = [

    Trade(direction="BUY", entry_time=None, profit=10),

    Trade(direction="BUY", entry_time=None, profit=20),

    Trade(direction="SELL", entry_time=None, profit=-5),

    Trade(direction="SELL", entry_time=None, profit=-15),

]

stats = calculate_statistics(trades)

assert stats["total_trade"] == 4
assert stats["winner"] == 2
assert stats["loser"] == 2
assert stats["gross_profit"] == 30
assert stats["gross_loss"] == 20
assert stats["net_profit"] == 10
assert stats["profit_factor"] == 1.5
assert stats["average_win"] == 15
assert stats["average_loss"] == 10
assert stats["expectancy"] == 2.5
assert stats["max_win"] == 20
assert stats["max_loss"] == -15
assert stats["average_rr"] == 1.5

print("=" * 50)
print("STATISTICS TEST PASSED")
print("=" * 50)

print()

for k, v in stats.items():
    print(f"{k:20}: {v}")