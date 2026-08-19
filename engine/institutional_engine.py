
"""
==========================================
SULTAN QUANT OS
Institutional Engine
Version : 5.2.1
==========================================

Responsibilities:

- Execute complete institutional pipeline
- Generate reports
- Generate Monte Carlo
- Generate Walk Forward Optimization
- Generate Risk Dashboard
- Generate Institutional Report
- Generate Portfolio Allocation
- Generate Portfolio Decision
"""

from pathlib import Path

from config.settings import DEFAULT_STRATEGY

from config.wfo_settings import (
    WFO_CONFIG,
    WFO_PARAMETER_GRID,
)

from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy
from engine.backtest_engine import run_backtest
from engine.statistics_engine import calculate_statistics
from engine.trade_logger import save_trade_journal
from engine.visual_engine import generate_visual_reports

from engine.portfolio_engine import (
    run_portfolio,
    get_best_strategy,
)

from reports.report_engine import generate_report
from reports.report_writer import save_report
from reports.html_report import generate_html_report

from optimizer.monte_carlo import run_monte_carlo
from optimizer.monte_carlo_analyzer import analyze_monte_carlo

from optimizer.wfo_runner import run_wfo

from optimizer.risk_dashboard import (
    build_risk_dashboard,
)

from reports.institutional_report_engine import (
    build_institutional_report,
)


# ==================================================
# OUTPUT
# ==================================================

OUTPUT_DIR = Path(
    "reports/output"
)

REPORT_FILE = (
    OUTPUT_DIR /
    "backtest_report.txt"
)

TRADE_FILE = (
    OUTPUT_DIR /
    "trade_journal.csv"
)


# ==================================================
# BACKTEST PIPELINE
# ==================================================

def run_backtest_pipeline(
    data_file: str,
):

    df = load_data(
        data_file
    )

    df = calculate_indicators(
        df
    )

    df = run_strategy(
        df,
        strategy=DEFAULT_STRATEGY,
    )

    trades = run_backtest(
        df
    )

    statistics = calculate_statistics(
        trades
    )

    return {

        "data":
            df,

        "trades":
            trades,

        "statistics":
            statistics,

    }

# ==================================================
# PORTFOLIO PIPELINE
# ==================================================

def run_portfolio_pipeline(
    data_file,
):

    from engine.allocation_engine import (
        build_allocation,
    )

    from engine.decision_engine import (
        evaluate_decision,
    )

    from risk.portfolio_risk import (
        calculate_portfolio_risk,
    )

    # ------------------------------------------
    # LOAD DATA
    # ------------------------------------------

    df = load_data(
        data_file,
    )

    df = calculate_indicators(
        df,
    )

    # ------------------------------------------
    # RUN PORTFOLIO
    # ------------------------------------------

    results = run_portfolio(
        df,
    )

    if results is None:
        results = []

    # ------------------------------------------
    # NORMALIZE PORTFOLIO RESULTS
    #
    # Strategy Ranker v3 preserves evaluation_status.
    # This layer guarantees backward compatibility with
    # older portfolio result objects.
    # ------------------------------------------

    normalized_results = []

    for item in results:

        if not isinstance(
            item,
            dict,
        ):
            continue

        result = item.copy()

        # --------------------------------------
        # Evaluation status
        # --------------------------------------

        if not result.get(
            "evaluation_status"
        ):

            statistics = result.get(
                "statistics",
                {},
            )

            trades = result.get(
                "trades",
                None,
            )

            if result.get(
                "error"
            ):

                result[
                    "evaluation_status"
                ] = "FAILED"

            elif isinstance(
                statistics,
                dict,
            ) and (
                statistics.get(
                    "total_trade",
                    statistics.get(
                        "total_trades",
                        None,
                    ),
                )
                is not None
            ):

                total_trade = statistics.get(
                    "total_trade",
                    statistics.get(
                        "total_trades",
                        0,
                    ),
                )

                try:

                    total_trade = int(
                        float(
                            total_trade
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    total_trade = 0

                if total_trade > 0:

                    result[
                        "evaluation_status"
                    ] = "SUCCESS"

                else:

                    result[
                        "evaluation_status"
                    ] = (
                        "INSUFFICIENT_DATA"
                    )

            elif trades is not None:

                try:

                    if len(trades) > 0:

                        result[
                            "evaluation_status"
                        ] = "SUCCESS"

                    else:

                        result[
                            "evaluation_status"
                        ] = (
                            "INSUFFICIENT_DATA"
                        )

                except TypeError:

                    result[
                        "evaluation_status"
                    ] = (
                        "INSUFFICIENT_DATA"
                    )

            else:

                result[
                    "evaluation_status"
                ] = (
                    "INSUFFICIENT_DATA"
                )

        # --------------------------------------
        # Safe defaults
        # --------------------------------------

        result.setdefault(
            "rank",
            0,
        )

        result.setdefault(
            "score",
            0,
        )

        result.setdefault(
            "grade",
            "N/A",
        )

        result.setdefault(
            "market_regime",
            "UNKNOWN",
        )

        result.setdefault(
            "weight",
            0,
        )

        result.setdefault(
            "router_recommended",
            False,
        )

        normalized_results.append(
            result
        )

    results = normalized_results

    # ------------------------------------------
    # BEST STRATEGY
    #
    # Only SUCCESS strategies are eligible.
    # Rank 1 should normally be the best.
    # ------------------------------------------

    best = get_best_strategy(
        results,
    )

    # ------------------------------------------
    # HARD FALLBACK
    #
    # Protect against legacy get_best_strategy()
    # implementations that may not recognize the
    # normalized status.
    # ------------------------------------------

    if best is None:

        successful = [

            item

            for item in results

            if item.get(
                "evaluation_status"
            ) == "SUCCESS"

        ]

        if successful:

            successful.sort(
                key=lambda item: (
                    float(
                        item.get(
                            "score",
                            0,
                        )
                    ),
                    float(
                        item.get(
                            "profit_factor",
                            item.get(
                                "statistics",
                                {},
                            ).get(
                                "profit_factor",
                                0,
                            ),
                        )
                    ),
                    -float(
                        item.get(
                            "drawdown",
                            item.get(
                                "statistics",
                                {},
                            ).get(
                                "max_drawdown_percent",
                                100,
                            ),
                        )
                    ),
                ),
                reverse=True,
            )

            best = successful[0]

    # ------------------------------------------
    # PORTFOLIO ALLOCATION
    # ------------------------------------------

    allocation = build_allocation(
        results,
    )

    # ------------------------------------------
    # PORTFOLIO RISK
    # ------------------------------------------

    risk = calculate_portfolio_risk(
        allocation,
    )

    # ------------------------------------------
    # PORTFOLIO DECISION
    # ------------------------------------------

    decision = evaluate_decision(
        risk,
        results,
    )

    # ------------------------------------------
    # RETURN
    # ------------------------------------------

    return {

        "portfolio":
            results,

        "best":
            best,

        "allocation":
            allocation,

        "risk":
            risk,

        "decision":
            decision,

    }

# ==================================================
# REPORTS
# ==================================================

def generate_reports(
    statistics,
    trades,
):

    report = generate_report(
        statistics
    )

    save_report(
        report,
        str(REPORT_FILE),
    )

    html_report = generate_html_report(
        statistics
    )

    save_trade_journal(
        trades,
        str(TRADE_FILE),
    )

    visual_files = generate_visual_reports(
        statistics,
        trades,
    )

    return {

        "text_report":
            REPORT_FILE,

        "html_report":
            html_report,

        "trade_journal":
            TRADE_FILE,

        "visual_files":
            visual_files,

    }


# ==================================================
# MONTE CARLO
# ==================================================

def run_monte_carlo_pipeline(
    trades,
):

    simulations = run_monte_carlo(
        trades,
        simulations=1000,
        initial_balance=10000,
        method="bootstrap",
        seed=42,
    )

    analysis = analyze_monte_carlo(
        simulations
    )

    return {

        "simulation":
            simulations,

        "analysis":
            analysis,

    }


# ==================================================
# WFO
# ==================================================

def run_wfo_pipeline(
    data_file,
):

    return run_wfo(
        data_file=data_file,
        parameter_grid=WFO_PARAMETER_GRID,
        config=WFO_CONFIG,
    )


# ==================================================
# RISK DASHBOARD
# ==================================================

def run_risk_pipeline(
    statistics,
    wfo_analysis,
    monte_carlo_analysis,
):

    return build_risk_dashboard(
        statistics,
        wfo_analysis,
        monte_carlo_analysis,
    )


# ==================================================
# INSTITUTIONAL REPORT
# ==================================================

def run_institutional_report(
    statistics,
    portfolio,
    monte_carlo,
    wfo,
    risk,
):

    return build_institutional_report(
        statistics=statistics,
        portfolio=portfolio,
        monte_carlo=monte_carlo,
        wfo=wfo,
        risk=risk,
    )


# ==================================================
# COMPLETE PIPELINE
# ==================================================

def execute_pipeline(
    data_file,
):

    # ------------------------------------------
    # BACKTEST
    # ------------------------------------------

    backtest = run_backtest_pipeline(
        data_file
    )

    statistics = backtest["statistics"]

    trades = backtest["trades"]

    # ------------------------------------------
    # PORTFOLIO
    # ------------------------------------------

    portfolio = run_portfolio_pipeline(
        data_file,
    )

    # ------------------------------------------
    # REPORTS
    # ------------------------------------------

    reports = generate_reports(
        statistics,
        trades,
    )

    # ------------------------------------------
    # MONTE CARLO
    # ------------------------------------------

    monte = run_monte_carlo_pipeline(
        trades
    )

    # ------------------------------------------
    # WALK FORWARD
    # ------------------------------------------

    wfo = run_wfo_pipeline(
        data_file
    )

    # ------------------------------------------
    # RISK DASHBOARD
    # ------------------------------------------

    risk = run_risk_pipeline(
        statistics,
        wfo["analysis"],
        monte["analysis"],
    )

    # ------------------------------------------
    # INSTITUTIONAL REPORT
    # ------------------------------------------

    institutional = run_institutional_report(
        statistics,
        portfolio,
        monte["analysis"],
        wfo["analysis"],
        risk,
    )

    # ------------------------------------------
    # FINAL RESULT
    # ------------------------------------------

    return {

        "statistics":
            statistics,

        "portfolio":
            portfolio,

        "reports":
            reports,

        "monte_carlo":
            monte,

        "wfo":
            wfo,

        "risk":
            risk,

        "institutional":
            institutional,

    }


# ==================================================
# PUBLIC API
# ==================================================

def run_institutional(
    data_file: str,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = execute_pipeline(
        data_file
    )

    # ==================================================
    # HEADER
    # ==================================================

    print()

    print("=" * 60)
    print("SULTAN QUANT OS")
    print("INSTITUTIONAL MODE")
    print("=" * 60)

    # ==================================================
    # PERFORMANCE
    # ==================================================

    print()

    print("PERFORMANCE")

    for key, value in result["statistics"].items():

        if key in [
            "equity_curve",
            "drawdown_curve",
        ]:

            continue

        print(
            f"{key:25}: {value}"
        )

    # ==================================================
    # GENERATED REPORTS
    # ==================================================

    print()

    print("=" * 60)
    print("GENERATED REPORTS")
    print("=" * 60)

    print(
        f"Text Report        : "
        f"{result['reports']['text_report']}"
    )

    print(
        f"HTML Report        : "
        f"{result['reports']['html_report']}"
    )

    print(
        f"Trade Journal      : "
        f"{result['reports']['trade_journal']}"
    )

    # ==================================================
    # VISUAL REPORTS
    # ==================================================

    print()

    print("VISUAL REPORTS")

    for file in result["reports"]["visual_files"]:

        print(
            f" - {file}"
        )

    # ==================================================
    # MONTE CARLO
    # ==================================================

    print()

    print("=" * 60)
    print("MONTE CARLO")
    print("=" * 60)

    for key, value in result["monte_carlo"]["analysis"].items():

        print(
            f"{key:25}: {value}"
        )

    # ==================================================
    # WALK FORWARD
    # ==================================================

    print()

    print("=" * 60)
    print("WALK FORWARD")
    print("=" * 60)

    for key, value in result["wfo"]["analysis"].items():

        print(
            f"{key:25}: {value}"
        )

    # ==================================================
    # RISK DASHBOARD
    # ==================================================

    print()

    print("=" * 60)
    print("RISK DASHBOARD")
    print("=" * 60)

    for key, value in result["risk"].items():

        print(
            f"{key:25}: {value}"
        )

    # ==================================================
    # PORTFOLIO
    # ==================================================

    portfolio_data = result["portfolio"]

    # ==================================================
    # BEST STRATEGY
    # ==================================================

    print()

    print("=" * 60)
    print("BEST STRATEGY")
    print("=" * 60)

    best = portfolio_data.get(
        "best"
    )

    if best:

        if isinstance(best, dict):

            print(
                f"Strategy             : "
                f"{best.get('name', 'UNKNOWN')}"
            )

            statistics = best.get(
                "statistics",
                {},
            )

            print(
                f"Profit Factor        : "
                f"{statistics.get('profit_factor', 0)}"
            )

            print(
                f"Win Rate             : "
                f"{statistics.get('win_rate', 0)}"
            )

            print(
                f"Rank                 : "
                f"{best.get('rank', 0)}"
            )

            print(
                f"Score                : "
                f"{best.get('score', 0)}"
            )

        else:

            print(
                f"Strategy             : "
                f"{best}"
            )

    else:

        print("No Best Strategy")

    # ==================================================
    # PORTFOLIO ALLOCATION
    # ==================================================

    print()

    print("=" * 60)
    print("PORTFOLIO ALLOCATION")
    print("=" * 60)

    allocation = portfolio_data.get(
        "allocation",
        [],
    )

    if allocation:

        if isinstance(allocation, dict):

            for name, weight in allocation.items():

                try:

                    print(
                        f"{name:25}: "
                        f"{float(weight) * 100:.2f}%"
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    print(
                        f"{name:25}: "
                        f"{weight}"
                    )

        else:

            for item in allocation:

                if not isinstance(
                    item,
                    dict,
                ):

                    print(
                        f" - {item}"
                    )

                    continue

                name = item.get(
                    "name",
                    "UNKNOWN",
                )

                weight = item.get(
                    "allocation",
                    item.get(
                        "weight",
                        0,
                    ),
                )

                try:

                    percentage = (
                        float(weight) * 100
                    )

                    print(
                        f"{name:25}: "
                        f"{percentage:.2f}%"
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    print(
                        f"{name:25}: "
                        f"{weight}"
                    )

    else:

        print("No Allocation")

    # ==================================================
    # PORTFOLIO RISK
    # ==================================================

    print()

    print("=" * 60)
    print("PORTFOLIO RISK")
    print("=" * 60)

    portfolio_risk = portfolio_data.get(
        "risk",
        {},
    )

    if portfolio_risk:

        if isinstance(
            portfolio_risk,
            dict,
        ):

            for key, value in portfolio_risk.items():

                print(
                    f"{key:25}: {value}"
                )

        else:

            print(
                portfolio_risk
            )

    else:

        print("No Portfolio Risk")

    # ==================================================
    # PORTFOLIO DECISION
    # ==================================================

    print()

    print("=" * 60)
    print("PORTFOLIO DECISION")
    print("=" * 60)

    decision = portfolio_data.get(
        "decision",
        {},
    )

    if decision:

        if isinstance(
            decision,
            dict,
        ):

            for key, value in decision.items():

                print(
                    f"{key:25}: {value}"
                )

        else:

            print(
                decision
            )

    else:

        print("No Decision")

    # ==================================================
    # PORTFOLIO SUMMARY
    # ==================================================

    portfolio_results = portfolio_data.get(
        "portfolio",
        [],
    )

    print()

    print("=" * 60)
    print("PORTFOLIO SUMMARY")
    print("=" * 60)

    if portfolio_results:

        print(
            f"Strategies Evaluated  : "
            f"{len(portfolio_results)}"
        )

        for index, item in enumerate(
            portfolio_results,
            start=1,
        ):

            name = item.get(
                "name",
                "UNKNOWN",
            )

            score = item.get(
                "score",
                0,
            )

            rank = item.get(
                "rank",
                index,
            )

            statistics = item.get(
                "statistics",
                {},
            )

            profit_factor = statistics.get(
                "profit_factor",
                0,
            )

            win_rate = statistics.get(
                "win_rate",
                0,
            )

            print(
                f"{rank:02d}. "
                f"{name:20} "
                f"Score={score} "
                f"PF={profit_factor} "
                f"WR={win_rate}"
            )

    else:

        print("No Portfolio Results")

    # ==================================================
    # INSTITUTIONAL REPORT
    # ==================================================

    print()

    print("=" * 60)
    print("INSTITUTIONAL REPORT")
    print("=" * 60)

    institutional = result["institutional"]

    if isinstance(
        institutional,
        dict,
    ):

        for key, value in institutional.items():

            print(
                f"{key:25}: {value}"
            )

    else:

        print(
            institutional
        )

    # ==================================================
    # COMPLETE
    # ==================================================

    print()

    print("=" * 60)
    print("SULTAN QUANT OS INSTITUTIONAL COMPLETE")
    print("=" * 60)

    return result


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    run_institutional(
        "data/XAUUSDc_M1.csv"
    )
