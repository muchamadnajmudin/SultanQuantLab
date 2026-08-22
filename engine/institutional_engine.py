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

Architecture:

This module acts as the high-level institutional
pipeline and backward-compatible entry point.

Institutional portfolio orchestration is owned by:

    engine.institutional_portfolio_engine
"""

from pathlib import Path


# ==================================================
# CONFIG
# ==================================================

from config.settings import DEFAULT_STRATEGY

from config.wfo_settings import (
    WFO_CONFIG,
    WFO_PARAMETER_GRID,
)


# ==================================================
# CORE ENGINES
# ==================================================

from engine.loader import load_data

from engine.indicator_engine import (
    calculate_indicators,
)

from engine.strategy_engine import (
    run_strategy,
)

from engine.backtest_engine import (
    run_backtest,
)

from engine.statistics_engine import (
    calculate_statistics,
)

from engine.trade_logger import (
    save_trade_journal,
)

from engine.visual_engine import (
    generate_visual_reports,
)


# ==================================================
# PORTFOLIO ENGINE
# ==================================================

from engine.portfolio_engine import (
    run_portfolio,
)

from engine.institutional_portfolio_engine import (
    build_institutional_portfolio,
)


# ==================================================
# REPORTS
# ==================================================

from reports.report_engine import (
    generate_report,
)

from reports.report_writer import (
    save_report,
)

from reports.html_report import (
    generate_html_report,
)


# ==================================================
# MONTE CARLO
# ==================================================

from optimizer.monte_carlo import (
    run_monte_carlo,
)

from optimizer.monte_carlo_analyzer import (
    analyze_monte_carlo,
)


# ==================================================
# WALK FORWARD OPTIMIZATION
# ==================================================

from optimizer.wfo_runner import (
    run_wfo,
)


# ==================================================
# RISK DASHBOARD
# ==================================================

from optimizer.risk_dashboard import (
    build_risk_dashboard,
)


# ==================================================
# INSTITUTIONAL REPORT
# ==================================================

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

    """
    Execute the standard backtest pipeline.

    Steps:

        1. Load market data
        2. Calculate indicators
        3. Execute default strategy
        4. Run backtest
        5. Calculate statistics
    """

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
    top_n=3,
):

    """
    Execute the institutional portfolio pipeline.

    This function remains the high-level compatibility
    entry point for file-based portfolio execution.

    Portfolio orchestration is delegated to:

        engine.institutional_portfolio_engine

    Responsibilities of this wrapper:

        1. Load market data
        2. Calculate indicators
        3. Delegate institutional portfolio orchestration

    The institutional portfolio engine is the single
    source of truth for:

        - Strategy evaluation
        - Portfolio result normalization
        - Best strategy selection
        - Portfolio allocation
        - Portfolio risk
        - Institutional decision
        - Portfolio exposure
        - Portfolio summary

    Parameters
    ----------
    data_file : str or path-like
        Market data file.

    top_n : int
        Maximum number of strategies forwarded to the
        allocation engine.

    Returns
    -------
    dict
        Institutional portfolio contract.
    """

    # ==================================================
    # LOAD DATA
    # ==================================================

    df = load_data(
        data_file,
    )

    # ==================================================
    # CALCULATE INDICATORS
    # ==================================================

    df = calculate_indicators(
        df,
    )

    # ==================================================
    # INSTITUTIONAL PORTFOLIO ORCHESTRATION
    # ==================================================

    return build_institutional_portfolio(
        df,
        top_n=top_n,
    )


# ==================================================
# REPORTS
# ==================================================

def generate_reports(
    statistics,
    trades,
):

    """
    Generate standard reports and trade journal.
    """

    report = generate_report(
        statistics
    )

    save_report(
        report,
        str(
            REPORT_FILE
        ),
    )

    html_report = generate_html_report(
        statistics
    )

    save_trade_journal(
        trades,
        str(
            TRADE_FILE
        ),
    )

    return {

        "report":
            report,

        "html_report":
            html_report,

        "report_file":
            str(
                REPORT_FILE
            ),

        "trade_file":
            str(
                TRADE_FILE
            ),

    }


# ==================================================
# MONTE CARLO PIPELINE
# ==================================================

def run_monte_carlo_pipeline(
    trades,
):

    """
    Execute Monte Carlo analysis.
    """

    monte_carlo = run_monte_carlo(
        trades
    )

    analysis = analyze_monte_carlo(
        monte_carlo
    )

    return {

        "simulation":
            monte_carlo,

        "analysis":
            analysis,

    }


# ==================================================
# WALK FORWARD PIPELINE
# ==================================================

def run_wfo_pipeline(
    df,
):

    """
    Execute Walk Forward Optimization.
    """

    return run_wfo(
        df,
        config=WFO_CONFIG,
        parameter_grid=WFO_PARAMETER_GRID,
    )


# ==================================================
# RISK PIPELINE
# ==================================================

def run_risk_pipeline(
    statistics,
    monte_carlo=None,
    wfo=None,
):

    """
    Build institutional risk dashboard.
    """

    return build_risk_dashboard(
        statistics,
        monte_carlo=monte_carlo,
        wfo=wfo,
    )


# ==================================================
# INSTITUTIONAL REPORT
# ==================================================

def run_institutional_report(
    portfolio,
    statistics,
    monte_carlo=None,
    wfo=None,
    risk_dashboard=None,
):

    """
    Build the final institutional report.
    """

    return build_institutional_report(
        portfolio=portfolio,
        statistics=statistics,
        monte_carlo=monte_carlo,
        wfo=wfo,
        risk_dashboard=risk_dashboard,
    )


# ==================================================
# COMPLETE INSTITUTIONAL PIPELINE
# ==================================================

def execute_pipeline(
    data_file,
):

    """
    Execute the complete institutional pipeline.

    Flow:

        Data
          ↓
        Indicators
          ↓
        Portfolio
          ↓
        Best Strategy
          ↓
        Backtest
          ↓
        Statistics
          ↓
        Monte Carlo
          ↓
        Walk Forward Optimization
          ↓
        Risk Dashboard
          ↓
        Institutional Report
    """

    # ==================================================
    # PORTFOLIO
    # ==================================================

    portfolio_result = run_portfolio_pipeline(
        data_file
    )

    portfolio = portfolio_result.get(
        "portfolio",
        [],
    )

    best = portfolio_result.get(
        "best"
    )

    # ==================================================
    # LOAD DATA
    # ==================================================

    df = load_data(
        data_file
    )

    df = calculate_indicators(
        df
    )

    # ==================================================
    # BEST STRATEGY FALLBACK
    # ==================================================

    if best and isinstance(
        best,
        dict,
    ):

        strategy_name = best.get(
            "name",
            DEFAULT_STRATEGY,
        )

    else:

        strategy_name = DEFAULT_STRATEGY

    # ==================================================
    # RUN STRATEGY
    # ==================================================

    strategy_df = run_strategy(
        df,
        strategy=strategy_name,
    )

    # ==================================================
    # BACKTEST
    # ==================================================

    trades = run_backtest(
        strategy_df
    )

    statistics = calculate_statistics(
        trades
    )

    # ==================================================
    # REPORTS
    # ==================================================

    reports = generate_reports(
        statistics,
        trades,
    )

    # ==================================================
    # MONTE CARLO
    # ==================================================

    monte_carlo = run_monte_carlo_pipeline(
        trades
    )

    # ==================================================
    # WALK FORWARD OPTIMIZATION
    # ==================================================

    wfo = run_wfo_pipeline(
        df
    )

    # ==================================================
    # RISK DASHBOARD
    # ==================================================

    risk_dashboard = run_risk_pipeline(
        statistics,
        monte_carlo=monte_carlo,
        wfo=wfo,
    )

    # ==================================================
    # INSTITUTIONAL REPORT
    # ==================================================

    institutional_report = run_institutional_report(
        portfolio=portfolio_result,
        statistics=statistics,
        monte_carlo=monte_carlo,
        wfo=wfo,
        risk_dashboard=risk_dashboard,
    )

    # ==================================================
    # RETURN
    # ==================================================

    return {

        "portfolio":
            portfolio,

        "portfolio_result":
            portfolio_result,

        "best":
            best,

        "data":
            df,

        "trades":
            trades,

        "statistics":
            statistics,

        "reports":
            reports,

        "monte_carlo":
            monte_carlo,

        "wfo":
            wfo,

        "risk_dashboard":
            risk_dashboard,

        "institutional_report":
            institutional_report,

    }


# ==================================================
# BACKWARD-COMPATIBLE INSTITUTIONAL ENTRY POINT
# ==================================================

def run_institutional(
    data_file,
):

    """
    Backward-compatible entry point for the complete
    institutional pipeline.
    """

    return execute_pipeline(
        data_file
    )