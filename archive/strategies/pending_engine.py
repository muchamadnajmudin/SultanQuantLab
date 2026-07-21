"""
==========================================
Sultan Quant Lab
Module : Pending Order Engine
Version : 0.1 Alpha
==========================================
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PendingOrder:
    direction: str
    signal_time: datetime
    execute_next_bar: bool = True