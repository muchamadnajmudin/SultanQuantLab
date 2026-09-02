"""
==========================================
SULTAN QUANT OS
WFO Runner
Version : 5.2.0
==========================================

Responsibilities:

- Execute Walk Forward Optimization
- Analyze WFO results
- Generate Advanced WFO Report
- Export JSON
- Export CSV
- Generate Visual Analytics
- Provide a stable orchestration contract

Design principles:

- Runner is an orchestrator only.
- WFO execution remains in optimizer.walk_forward.
- WFO analysis remains in optimizer.wfo_analyzer.
- Reporting remains in reports modules.
- Visualization remains in engine.wfo_visual_engine.
- Existing return keys are preserved.
- Grid modules are not touched.

Backward-compatible return keys:

- results
- analysis
- report
- report_file
- result_file
- csv_file
- visual_files

Additional metadata:

- data_file
- parameter_grid
- config

==========================================
"""


from pathlib import Path
import json
from copy import deepcopy


from optimizer.walk_forward import (
    run_walk_forward,
)


from optimizer.wfo_analyzer import (
    analyze_wfo,
)


from reports.wfo_report_engine import (
    generate_wfo_advanced_report,
)


from reports.wfo_csv_exporter import (
    export_wfo_csv,
)


from engine.wfo_visual_engine import (
    generate_wfo_visual_reports,
)


# ==================================================
# OUTPUT
# ==================================================

OUTPUT_DIR = Path(
    "reports/output"
)


WFO_REPORT_FILE = (
    OUTPUT_DIR
    /
    "wfo_report.txt"
)


WFO_RESULT_FILE = (
    OUTPUT_DIR
    /
    "wfo_results.json"
)


# ==================================================
# DEFAULT PARAMETER
# ==================================================

DEFAULT_PARAMETER_GRID = {

    "RSI_OVERSOLD": [

        5,
        10,
        15,

    ],

    "RSI_OVERBOUGHT": [

        85,
        90,
        95,

    ],

}


# ==================================================
# DIRECTORY
# ==================================================

def prepare_output_directory(
    directory=OUTPUT_DIR,
):
    """
    Ensure an output directory exists.

    Parameters
    ----------
    directory : str | Path
        Directory to create.

    Returns
    -------
    Path
        Normalized output directory.
    """

    output = Path(
        directory
    )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output


# ==================================================
# SAVE JSON
# ==================================================

def save_wfo_results(
    results,
    filename=WFO_RESULT_FILE,
):
    """
    Save WFO results as JSON.

    The parent directory of a custom filename is also
    created automatically.

    Parameters
    ----------
    results : object
        WFO result collection.

    filename : str | Path
        Destination JSON file.

    Returns
    -------
    Path
        Saved file path.
    """

    output = Path(
        filename
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            default=str,
        )

    return output


# ==================================================
# SAVE REPORT
# ==================================================

def save_wfo_report(
    report,
    filename=WFO_REPORT_FILE,
):
    """
    Save WFO text report.

    The parent directory of a custom filename is also
    created automatically.

    Parameters
    ----------
    report : str
        Generated report text.

    filename : str | Path
        Destination report file.

    Returns
    -------
    Path
        Saved file path.
    """

    output = Path(
        filename
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        str(report),
        encoding="utf-8",
    )

    return output


# ==================================================
# NORMALIZE PARAMETER GRID
# ==================================================

def _prepare_parameter_grid(
    parameter_grid,
):
    """
    Prepare an isolated parameter grid.

    A deep copy prevents downstream optimization code from
    accidentally mutating DEFAULT_PARAMETER_GRID or a grid
    supplied by the caller.
    """

    if parameter_grid is None:

        return deepcopy(
            DEFAULT_PARAMETER_GRID
        )

    return deepcopy(
        parameter_grid
    )


# ==================================================
# NORMALIZE RESULTS
# ==================================================

def _normalize_results(
    results,
):
    """
    Normalize the WFO execution result.

    The runner expects a list-like collection of window
    results. A None result is treated as an empty result.

    This function deliberately does not fabricate WFO
    windows or performance data.
    """

    if results is None:

        return []

    if isinstance(
        results,
        list,
    ):

        return results

    try:

        return list(
            results
        )

    except TypeError:

        return []


# ==================================================
# MAIN RUNNER
# ==================================================

def run_wfo(
    data_file,
    parameter_grid=None,
    config=None,
):
    """
    Execute the complete WFO research pipeline.

    Pipeline:

        1. Walk Forward Optimization
        2. WFO Analysis
        3. Advanced Report
        4. JSON Export
        5. CSV Export
        6. Visual Analytics

    Parameters
    ----------
    data_file : str | Path
        Historical market data.

    parameter_grid : dict | None
        Optimization parameter grid.

    config : dict | None
        WFO execution configuration.

    Returns
    -------
    dict
        Stable WFO runner result contract.
    """

    # ==================================================
    # PREPARE INPUTS
    # ==================================================

    prepared_parameter_grid = (
        _prepare_parameter_grid(
            parameter_grid
        )
    )

    prepared_config = (
        deepcopy(config)
        if config is not None
        else None
    )


    # ==================================================
    # PREPARE OUTPUT DIRECTORY
    # ==================================================

    prepare_output_directory()


    # ==================================================
    # WALK FORWARD
    # ==================================================

    results = run_walk_forward(

        data_file=data_file,

        parameter_grid=(
            prepared_parameter_grid
        ),

        config=(
            prepared_config
        ),

    )


    # ==================================================
    # NORMALIZE RESULTS
    # ==================================================

    results = _normalize_results(
        results
    )


    # ==================================================
    # ANALYSIS
    # ==================================================

    analysis = analyze_wfo(
        results
    )


    # ==================================================
    # ADVANCED REPORT
    # ==================================================

    report = (
        generate_wfo_advanced_report(

            analysis,

            results,

        )
    )


    # ==================================================
    # SAVE REPORT
    # ==================================================

    report_file = save_wfo_report(
        report
    )


    # ==================================================
    # SAVE JSON
    # ==================================================

    result_file = save_wfo_results(
        results
    )


    # ==================================================
    # EXPORT CSV
    # ==================================================

    csv_file = export_wfo_csv(
        results
    )


    # ==================================================
    # VISUAL REPORT
    # ==================================================

    visual_files = (
        generate_wfo_visual_reports(
            results
        )
    )


    # ==================================================
    # RETURN
    # ==================================================

    return {

        # --------------------------------------------------
        # Existing stable contract
        # --------------------------------------------------

        "results":

            results,

        "analysis":

            analysis,

        "report":

            report,

        "report_file":

            report_file,

        "result_file":

            result_file,

        "csv_file":

            csv_file,

        "visual_files":

            visual_files,

        # --------------------------------------------------
        # Additional metadata
        # --------------------------------------------------

        "data_file":

            Path(data_file),

        "parameter_grid":

            deepcopy(
                prepared_parameter_grid
            ),

        "config":

            deepcopy(
                prepared_config
            ),

    }


# ==================================================
# COMMAND-LINE TEST
# ==================================================

if __name__ == "__main__":

    output = run_wfo(

        data_file=(
            "data/XAUUSDc_M1.csv"
        ),

    )


    print()

    print(
        "=" * 50
    )

    print(
        "SULTAN QUANT OS"
    )

    print(
        "WFO RUNNER"
    )

    print(
        "=" * 50
    )


    print()

    print(
        "Analysis"
    )


    for key, value in (
        output[
            "analysis"
        ].items()
    ):

        print(

            f"{key:35}: "
            f"{value}"

        )


    print()

    print(
        "Generated Files"
    )


    print(

        f"Report : "
        f"{output['report_file']}"

    )


    print(

        f"JSON   : "
        f"{output['result_file']}"

    )


    print(

        f"CSV    : "
        f"{output['csv_file']}"

    )


    print()

    print(
        "Charts"
    )


    for file in (
        output[
            "visual_files"
        ]
    ):

        print(

            f" - {file}"

        )


    print()

    print(
        "WFO RUNNER COMPLETE"
    )