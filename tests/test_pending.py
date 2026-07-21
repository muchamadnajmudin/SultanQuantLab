from datetime import datetime

from engine.pending_engine import PendingOrder

order = PendingOrder(
    direction="BUY",
    signal_time=datetime.now()
)

print(order)