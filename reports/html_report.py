"""
==========================================
SULTAN QUANT OS
HTML Report Generator
Version : 2.4.0
==========================================
"""

from pathlib import Path
from datetime import datetime

from reports.report_template import HTML_TEMPLATE


# =====================================================
# CONFIG
# =====================================================

OUTPUT_DIR = Path(
    "reports/output"
)


HTML_FILE = (
    OUTPUT_DIR /
    "backtest_report.html"
)


# =====================================================
# FORMAT
# =====================================================

def _format(value):

    if isinstance(value, float):

        return round(value, 2)

    return value



# =====================================================
# BUILD HTML
# =====================================================

def generate_html_report(
    statistics: dict,
    filename: str = None
):


    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    html = HTML_TEMPLATE



    replacements = {

        "{{VERSION}}":
            "2.4.0",

        "{{STRATEGY}}":
            "XAUUSD Quant Strategy",

        "{{SYMBOL}}":
            "XAUUSD",

        "{{TIMEFRAME}}":
            "M1",

        "{{GENERATED}}":
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            ),


        "{{NET_PROFIT}}":
            str(
                _format(
                    statistics.get(
                        "net_profit",
                        0
                    )
                )
            ),


        "{{WIN_RATE}}":
            str(
                _format(
                    statistics.get(
                        "win_rate",
                        0
                    )
                )
            )
            + "%",


        "{{PROFIT_FACTOR}}":
            str(
                _format(
                    statistics.get(
                        "profit_factor",
                        0
                    )
                )
            ),


        "{{MAX_DRAWDOWN}}":
            str(
                _format(
                    statistics.get(
                        "max_drawdown",
                        0
                    )
                )
            ),


        "{{RECOVERY}}":
            str(
                _format(
                    statistics.get(
                        "recovery_factor",
                        0
                    )
                )
            ),


        "{{SHARPE}}":
            str(
                _format(
                    statistics.get(
                        "sharpe_ratio",
                        0
                    )
                )
            ),


        "{{WINNER}}":
            str(
                statistics.get(
                    "winner",
                    0
                )
            ),


        "{{LOSER}}":
            str(
                statistics.get(
                    "loser",
                    0
                )
            ),

    }



    for key, value in replacements.items():

        html = html.replace(
            key,
            value
        )



    if filename:

        output = Path(filename)

    else:

        output = HTML_FILE



    output.write_text(
        html,
        encoding="utf-8"
    )


    return output