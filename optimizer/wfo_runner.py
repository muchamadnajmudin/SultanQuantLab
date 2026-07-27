"""
==========================================
SULTAN QUANT OS
WFO Runner
Version : 5.0.1
==========================================

Responsibilities:

- Execute Walk Forward Optimization
- Run WFO Analyzer
- Generate WFO Report
- Save WFO result

"""

from pathlib import Path
import json


from optimizer.walk_forward import (
    run_walk_forward
)


from optimizer.wfo_analyzer import (
    analyze_wfo
)


from optimizer.wfo_report import (
    generate_wfo_report
)



# ==================================================
# CONFIG
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
# DEFAULT PARAMETER GRID
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
# SAVE JSON
# ==================================================

def save_wfo_results(
    results,
    filename=WFO_RESULT_FILE,
):


    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True

    )


    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as file:


        json.dump(

            results,

            file,

            indent=4,

            default=str

        )


    return filename



# ==================================================
# SAVE REPORT
# ==================================================

def save_wfo_report(

    report: str,

    filename=WFO_REPORT_FILE,

):


    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True

    )


    Path(filename).write_text(

        report,

        encoding="utf-8"

    )


    return filename



# ==================================================
# MAIN WFO RUNNER
# ==================================================

def run_wfo(

    data_file: str,

    parameter_grid=None,

    config=None,

):


    if parameter_grid is None:


        parameter_grid = (

            DEFAULT_PARAMETER_GRID

        )



    # ----------------------------------------------
    # RUN WALK FORWARD
    # ----------------------------------------------

    results = run_walk_forward(

        data_file=data_file,

        parameter_grid=parameter_grid,

        config=config,

    )



    # ----------------------------------------------
    # ANALYSIS
    # ----------------------------------------------

    analysis = analyze_wfo(

        results

    )



    # ----------------------------------------------
    # REPORT
    # ----------------------------------------------

    report = generate_wfo_report(

        analysis,

        results,

    )



    # ----------------------------------------------
    # SAVE
    # ----------------------------------------------

    result_file = save_wfo_results(

        results

    )


    report_file = save_wfo_report(

        report

    )



    return {

        "results":

            results,


        "analysis":

            analysis,


        "report":

            report,


        "result_file":

            result_file,


        "report_file":

            report_file,

    }



# ==================================================
# TEST RUN
# ==================================================

if __name__ == "__main__":


    output = run_wfo(

        data_file=

            "data/XAUUSDc_M1.csv"

    )


    print(output["analysis"])