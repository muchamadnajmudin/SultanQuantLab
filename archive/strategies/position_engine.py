"""
==========================================
Sultan Quant Lab
Module : Position Engine
Version : 0.1 Alpha
==========================================
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Position:
    direction: str
    entry_price: float
    entry_time: datetime
    stop_loss: float = 0.0
    take_profit: float = 0.0
    exit_price: float = 0.0
    exit_time: datetime | None = None
    profit: float = 0.0
    status: str = "OPEN"