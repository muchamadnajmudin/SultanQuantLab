"""
==========================================
SULTAN QUANT OS
Price Action Score
Version : 1.0.0
==========================================

Responsibilities

- Calculate Setup Score
- Calculate Confidence
- Trade Quality Grade

"""


# ==================================================
# SETUP SCORE
# ==================================================

def calculate_setup_score(

    confirmation_score,
    pattern_score,
    structure_score,
    rr_score,

):

    score = (

        confirmation_score
        + pattern_score
        + structure_score
        + rr_score

    )

    return min(100, round(score, 2))


# ==================================================
# CONFIDENCE
# ==================================================

def confidence_level(score):

    if score >= 90:
        return "VERY HIGH"

    if score >= 80:
        return "HIGH"

    if score >= 70:
        return "GOOD"

    if score >= 60:
        return "MEDIUM"

    return "LOW"


# ==================================================
# TRADE GRADE
# ==================================================

def trade_grade(score):

    if score >= 90:
        return "A+"

    if score >= 80:
        return "A"

    if score >= 70:
        return "B"

    if score >= 60:
        return "C"

    return "D"


# ==================================================
# PATTERN SCORE
# ==================================================

def pattern_score(

    engulfing=False,
    pinbar=False,
    insidebar=False,
    outsidebar=False,

):

    score = 0

    if engulfing:
        score += 25

    if pinbar:
        score += 20

    if insidebar:
        score += 15

    if outsidebar:
        score += 20

    return min(score, 30)


# ==================================================
# STRUCTURE SCORE
# ==================================================

def structure_score(

    bos=False,
    choch=False,
    mss=False,

):

    score = 0

    if bos:
        score += 20

    if choch:
        score += 20

    if mss:
        score += 20

    return min(score, 30)


# ==================================================
# RISK REWARD SCORE
# ==================================================

def rr_score(rr):

    if rr >= 3:

        return 20

    if rr >= 2:

        return 15

    if rr >= 1.5:

        return 10

    return 0