"""
==========================================
SULTAN QUANT OS
HTML Report Generator
Version : 4.5.0
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

        return round(
            value,
            2
        )

    return value



# =====================================================
# BUILD HTML
# =====================================================

def generate_html_report(
    statistics: dict,
    wfo_analysis: dict = None,
    monte_carlo_analysis: dict = None,
    risk_dashboard: dict = None,
    filename: str = None,
):


    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )



    html = HTML_TEMPLATE



    if wfo_analysis is None:

        wfo_analysis = {}



    if monte_carlo_analysis is None:

        monte_carlo_analysis = {}



    if risk_dashboard is None:

        risk_dashboard = {}



    replacements = {



        "{{VERSION}}":

            "4.5.0",



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

        "{{WFO_SCORE}}":

            str(
                _format(
                    wfo_analysis.get(
                        "wfo_score",
                        0
                    )
                )
            ),



        "{{WFO_STABILITY}}":

            str(
                _format(
                    wfo_analysis.get(
                        "stability",
                        0
                    )
                )
            ),



        "{{MC_RISK}}":

            str(
                _format(
                    monte_carlo_analysis.get(
                        "risk",
                        0
                    )
                )
            ),



        "{{MC_DRAWDOWN}}":

            str(
                _format(
                    monte_carlo_analysis.get(
                        "max_drawdown",
                        0
                    )
                )
            ),



        "{{QUALITY_SCORE}}":

            str(
                _format(
                    risk_dashboard.get(
                        "quality_score",
                        0
                    )
                )
            ),


    }



    for key, value in replacements.items():


        html = html.replace(

            key,

            value

        )



    if filename:


        output = Path(
            filename
        )


    else:


        output = HTML_FILE



    output.write_text(

        html,

        encoding="utf-8"

    )



    return str(output)            