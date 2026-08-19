from strategies.price_action_score import (
    calculate_setup_score,
    confidence_level,
    trade_grade,
)


def test_setup_score():

    score = calculate_setup_score(

        confirmation_score=30,
        pattern_score=25,
        structure_score=25,
        rr_score=20,

    )

    assert score == 100

    assert confidence_level(score) == "VERY HIGH"

    assert trade_grade(score) == "A+"