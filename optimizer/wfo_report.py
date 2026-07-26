"""
==========================================
SULTAN QUANT OS
WFO Report Generator
Version : 3.2.0
==========================================

Responsibilities:

- Generate WFO summary report
- Display validation results
- Summarize stability analysis

"""



# ==================================================
# FORMAT HEADER
# ==================================================

def header(title):

    return (
        "\n"
        + "=" * 50
        + "\n"
        + title
        + "\n"
        + "=" * 50
        + "\n"
    )



# ==================================================
# GENERATE REPORT
# ==================================================

def generate_wfo_report(
    analysis: dict,
    results: list[dict],
) -> str:


    if not analysis:

        return "EMPTY WFO REPORT"



    report = ""


    report += header(
        "SULTAN QUANT OS\nWFO REPORT"
    )


    report += (
        f"Windows Tested : "
        f"{analysis.get('total_window',0)}\n\n"
    )


    report += (
        f"Average Profit Factor : "
        f"{analysis.get('average_profit_factor',0)}\n"
    )


    report += (
        f"Average Net Profit    : "
        f"{analysis.get('average_net_profit',0)}\n"
    )


    report += (
        f"Stability Score       : "
        f"{analysis.get('stability_score',0)}%\n"
    )


    report += (
        f"Overfitting Risk      : "
        f"{analysis.get('overfitting_risk','UNKNOWN')}\n"
    )



    report += header(
        "WINDOW RESULTS"
    )



    for item in results:


        report += (
            f"\nWindow : "
            f"{item.get('window')}\n"
        )


        report += (
            f"Best Parameter : "
            f"{item.get('best_parameter')}\n"
        )


        validation = item.get(
            "validation",
            {}
        )


        report += (
            f"Validation PF : "
            f"{validation.get('profit_factor',0)}\n"
        )


        report += (
            f"Validation Net : "
            f"{validation.get('net_profit',0)}\n"
        )


        report += "-" * 30 + "\n"



    return report