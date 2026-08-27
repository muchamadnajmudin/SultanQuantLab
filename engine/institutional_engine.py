"""
==========================================
SULTAN QUANT OS
Institutional Engine
Version : 5.2.5
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

from config.settings import (
    DEFAULT_STRATEGY,
)

from config.wfo_settings import (
    WFO_CONFIG,
    WFO_PARAMETER_GRID,
)


# ==================================================
# CORE ENGINES
# ==================================================

from engine.loader import (
    load_data,
)

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
# STRATEGY NAME NORMALIZATION
# ==================================================

def _extract_strategy_name(
    best_strategy,
):

    """
    Extract the selected strategy name from a strategy
    result while preserving compatibility with possible
    strategy result contracts.

    Supported keys:

        - name
        - strategy
        - strategy_name

    Returns None when no valid strategy identifier
    is available.
    """

    if not isinstance(
        best_strategy,
        dict,
    ):

        return None


    strategy_name = (

        best_strategy.get(
            "name"
        )

        or best_strategy.get(
            "strategy"
        )

        or best_strategy.get(
            "strategy_name"
        )
    )


    if strategy_name is None:

        return None


    strategy_name = str(
        strategy_name
    ).strip()


    if not strategy_name:

        return None


    return strategy_name


# ==================================================
# STRATEGY SELECTION
# ==================================================

def _resolve_strategy_name(
    best_strategy,
):

    """
    Resolve the strategy used by the execution pipeline.

    Priority:

        1. Strategy selected by institutional portfolio
        2. DEFAULT_STRATEGY fallback

    This preserves backward compatibility while allowing
    portfolio selection to remain the primary source of
    strategy selection.
    """

    strategy_name = _extract_strategy_name(
        best_strategy
    )


    if strategy_name:

        return strategy_name


    return DEFAULT_STRATEGY


# ==================================================
# BACKTEST PIPELINE
# ==================================================

def run_backtest_pipeline(
    data_file,
):

    """
    Execute the standard backtest pipeline.
    """

    df = load_data(
        data_file
    )

    df = calculate_indicators(
        df
    )

    strategy_df = run_strategy(
        df,
        strategy=DEFAULT_STRATEGY,
    )

    trades = run_backtest(
        strategy_df
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
# INTERNAL PORTFOLIO FROM DATAFRAME
# ==================================================

def _run_portfolio_from_dataframe(
    df,
    top_n=3,
):

    """
    Execute institutional portfolio using an already
    prepared DataFrame.

    Prevents duplicate data loading and duplicate
    indicator calculation.
    """

    return build_institutional_portfolio(
        df,
        top_n=top_n,
    )


# ==================================================
# PORTFOLIO PIPELINE
# ==================================================

def run_portfolio_pipeline(
    data_file,
    top_n=3,
):

    """
    File-based compatibility entry point.
    """

    df = load_data(
        data_file
    )

    df = calculate_indicators(
        df
    )

    return _run_portfolio_from_dataframe(
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
    Generate standard text report,
    HTML report and trade journal.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


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
    Execute Monte Carlo simulation and analysis.
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
    Build final institutional report.

    portfolio must contain the complete institutional
    portfolio result contract.
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
    Execute complete institutional pipeline.

    Market data and indicators are prepared once
    and reused by all downstream operations.
    """


    # ==================================================
    # LOAD DATA
    # ==================================================

    df = load_data(
        data_file
    )


    # ==================================================
    # CALCULATE INDICATORS
    # ==================================================

    df = calculate_indicators(
        df
    )


    # ==================================================
    # INSTITUTIONAL PORTFOLIO
    # ==================================================

    portfolio_result = (
        _run_portfolio_from_dataframe(
            df
        )
    )


    strategy_results = (
        portfolio_result.get(
            "portfolio",
            [],
        )
    )


    best_strategy = (
        portfolio_result.get(
            "best"
        )
    )


    # ==================================================
    # SELECT STRATEGY
    #
    # The institutional portfolio is the primary source
    # of strategy selection. DEFAULT_STRATEGY is retained
    # as a backward-compatible fallback.
    # ==================================================

    strategy_name = _resolve_strategy_name(
        best_strategy
    )


    # ==================================================
    # RUN SELECTED STRATEGY
    #
    # Use a copy to prevent accidental mutation of the
    # shared prepared DataFrame.
    # ==================================================

    strategy_df = df.copy(
        deep=True
    )


    strategy_df = run_strategy(
        strategy_df,
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
    # VISUAL REPORTS
    # ==================================================

    try:

        visual_reports = (
            generate_visual_reports(
                trades
            )
        )

    except Exception:

        visual_reports = None


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

    institutional_report = (
        run_institutional_report(
            portfolio=portfolio_result,
            statistics=statistics,
            monte_carlo=monte_carlo,
            wfo=wfo,
            risk_dashboard=risk_dashboard,
        )
    )


    # ==================================================
    # RETURN COMPLETE CONTRACT
    # ==================================================

    return {

        "portfolio":
            strategy_results,

        "portfolio_result":
            portfolio_result,

        "best":
            best_strategy,

        "strategy_name":
            strategy_name,

        "data":
            df,

        "trades":
            trades,

        "statistics":
            statistics,

        "reports":
            reports,

        "visual_reports":
            visual_reports,

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
# BACKWARD-COMPATIBLE ENTRY POINT
# ==================================================

def run_institutional(
    data_file,
):

    """
    Backward-compatible entry point.
    """

    return execute_pipeline(
        data_file
    )


# ==================================================
# PUBLIC API
# ==================================================

__all__ = [

    "run_backtest_pipeline",

    "run_portfolio_pipeline",

    "generate_reports",

    "run_monte_carlo_pipeline",

    "run_wfo_pipeline",

    "run_risk_pipeline",

    "run_institutional_report",

    "execute_pipeline",

    "run_institutional",

]