"""
==========================================
SULTAN QUANT OS
Institutional Decision Report
Version : 4.2.0
==========================================

Responsibilities

- Generate Institutional Decision Report
- Return Report Text

"""


def generate_report(data):

    lines = []

    lines.append("=" * 50)
    lines.append("SULTAN QUANT OS")
    lines.append("INSTITUTIONAL DECISION REPORT")
    lines.append("=" * 50)
    lines.append("")

    # ------------------------------------------
    # MARKET REGIME
    # ------------------------------------------

    lines.append("MARKET REGIME")
    lines.append("-" * 50)

    lines.append(
        str(
            data.get(
                "regime",
                "UNKNOWN",
            )
        )
    )

    lines.append("")

    # ------------------------------------------
    # STRATEGY ALLOCATION
    # ------------------------------------------

    lines.append("STRATEGY ALLOCATION")
    lines.append("-" * 50)

    for item in data.get(
        "allocation",
        [],
    ):

        allocation = round(
            item.get(
                "allocation",
                0,
            )
            * 100,
            2,
        )

        lines.append(
            f"{item['name']:<25} {allocation:>6}%"
        )

    lines.append("")

    # ------------------------------------------
    # DECISION
    # ------------------------------------------

    decision = data.get(
        "decision",
        {},
    )

    lines.append("FINAL DECISION")
    lines.append("-" * 50)

    lines.append(
        f"Status      : {decision.get('decision', 'UNKNOWN')}"
    )

    lines.append(
        f"Strategy    : {decision.get('best_strategy', '-')}"
    )

    lines.append(
        f"ProfitFactor: {decision.get('profit_factor', 0)}"
    )

    lines.append(
        f"Drawdown    : {decision.get('drawdown', 0)}"
    )

    lines.append("=" * 50)

    return "\n".join(lines)