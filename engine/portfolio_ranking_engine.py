"""
==========================================
SULTAN QUANT OS
Portfolio Ranking Engine
Version : 1.0.0
==========================================

Responsibilities:

- Calculate strategy score
- Rank portfolio
- Return best strategy
- Print ranking

"""

# ==================================================
# CALCULATE SCORE
# ==================================================

def calculate_strategy_score(result):

    statistics = result.get("statistics", {})

    profit_factor = statistics.get("profit_factor", 0)
    sharpe = statistics.get("sharpe_ratio", 0)
    expectancy = statistics.get("expectancy", 0)
    win_rate = statistics.get("win_rate", 0)
    recovery = statistics.get("recovery_factor", 0)
    drawdown = statistics.get("max_drawdown_percent", 100)

    score = 0

    # ------------------------------------------
    # Profit Factor (30)
    # ------------------------------------------

    score += min(profit_factor * 15, 30)

    # ------------------------------------------
    # Sharpe Ratio (20)
    # ------------------------------------------

    score += min(sharpe * 10, 20)

    # ------------------------------------------
    # Expectancy (15)
    # ------------------------------------------

    score += min(expectancy * 5, 15)

    # ------------------------------------------
    # Win Rate (10)
    # ------------------------------------------

    score += min(win_rate / 10, 10)

    # ------------------------------------------
    # Recovery Factor (10)
    # ------------------------------------------

    score += min(recovery * 2, 10)

    # ------------------------------------------
    # Drawdown (15)
    # ------------------------------------------

    if drawdown <= 10:
        score += 15

    elif drawdown <= 20:
        score += 10

    elif drawdown <= 30:
        score += 5

    return round(score, 2)


# ==================================================
# RANK PORTFOLIO
# ==================================================

def rank_portfolio(results):

    ranked = []

    for result in results:

        item = result.copy()

        item["score"] = calculate_strategy_score(result)

        ranked.append(item)

    ranked.sort(

        key=lambda x: x["score"],

        reverse=True,

    )

    return ranked


# ==================================================
# BEST STRATEGY
# ==================================================

def get_best_strategy(results):

    ranked = rank_portfolio(results)

    if not ranked:

        return None

    return ranked[0]


# ==================================================
# PRINT RANKING
# ==================================================

def print_ranking(results):

    ranked = rank_portfolio(results)

    print()

    print("=" * 60)
    print("PORTFOLIO RANKING")
    print("=" * 60)

    for i, item in enumerate(ranked, start=1):

        print(

            f"{i:>2}. "

            f"{item['name']:<25}"

            f"Score : {item['score']}"

        )

    print()

    return ranked