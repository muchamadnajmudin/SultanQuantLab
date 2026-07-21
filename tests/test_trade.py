from datetime import datetime

from engine.trade import Trade

trade = Trade(

    direction="BUY",

    entry_time=datetime.now(),

    entry_price=4500,

    stop_loss=4495,

    take_profit=4510

)

print("=" * 50)
print("TRADE TEST")
print("=" * 50)

print(trade)