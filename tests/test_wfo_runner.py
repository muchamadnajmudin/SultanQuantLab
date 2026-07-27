"""
==========================================
SULTAN QUANT OS
Test WFO Runner
Version : 5.0.1
==========================================
"""

from optimizer.wfo_runner import run_wfo


def test_wfo_runner_import():

    assert callable(
        run_wfo
    )