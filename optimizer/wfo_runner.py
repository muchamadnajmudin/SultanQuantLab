"""
==========================================
SULTAN QUANT OS
WFO Runner
Version : 5.1.0
==========================================

Responsibilities:

- Execute Walk Forward Optimization
- Analyze WFO results
- Generate Advanced WFO Report
- Export JSON
- Export CSV
- Generate Visual Analytics

"""

from pathlib import Path
import json

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
    OUTPUT_DIR /
    "wfo_report.txt"
)

WFO_RESULT_FILE = (
    OUTPUT_DIR /
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

def prepare_output_directory():

    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )


# ==================================================
# SAVE JSON
# ==================================================

def save_wfo_results(

    results,

    filename=WFO_RESULT_FILE,

):

    prepare_output_directory()

    with open(

        filename,

        "w",

        encoding="utf-8",

    ) as file:

        json.dump(

            results,

            file,

            indent=4,

            default=str,

        )

    return Path(filename)


# ==================================================
# SAVE REPORT
# ==================================================

def save_wfo_report(

    report,

    filename=WFO_REPORT_FILE,

):

    prepare_output_directory()

    Path(filename).write_text(

        report,

        encoding="utf-8",

    )

    return Path(filename)

    # ==================================================
# MAIN RUNNER
# ==================================================

def run_wfo(

    data_file,

    parameter_grid=None,

    config=None,

):

    if parameter_grid is None:

        parameter_grid = DEFAULT_PARAMETER_GRID


    # ---------------------------------------------
    # WALK FORWARD
    # ---------------------------------------------

    results = run_walk_forward(

        data_file=data_file,

        parameter_grid=parameter_grid,

        config=config,

    )


    # ---------------------------------------------
    # ANALYSIS
    # ---------------------------------------------

    analysis = analyze_wfo(

        results

    )


    # ---------------------------------------------
    # ADVANCED REPORT
    # ---------------------------------------------

    report = generate_wfo_advanced_report(

        analysis,

        results,

    )


    # ---------------------------------------------
    # SAVE REPORT
    # ---------------------------------------------

    report_file = save_wfo_report(

        report

    )


    # ---------------------------------------------
    # SAVE JSON
    # ---------------------------------------------

    result_file = save_wfo_results(

        results

    )


    # ---------------------------------------------
    # EXPORT CSV
    # ---------------------------------------------

    csv_file = export_wfo_csv(

        results

    )


    # ---------------------------------------------
    # VISUAL REPORT
    # ---------------------------------------------

    visual_files = generate_wfo_visual_reports(

        results

    )


    # ---------------------------------------------
    # RETURN
    # ---------------------------------------------

    return {

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

    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    output = run_wfo(

        data_file="data/XAUUSDc_M1.csv",

    )

    print()

    print("=" * 50)
    print("SULTAN QUANT OS")
    print("WFO RUNNER")
    print("=" * 50)

    print()

    print("Analysis")

    for key, value in output["analysis"].items():

        print(

            f"{key:25}: {value}"

        )

    print()

    print("Generated Files")

    print(

        f"Report : {output['report_file']}"

    )

    print(

        f"JSON   : {output['result_file']}"

    )

    print(

        f"CSV    : {output['csv_file']}"

    )

    print()

    print("Charts")

    for file in output["visual_files"]:

        print(

            f" - {file}"

        )

    print()

    print("WFO RUNNER COMPLETE")