from strategies.ensemble.exposure_manager import (
    detect_duplicate,
    remove_duplicate,
)


def test_detect_duplicate():

    results = [

        {"name": "price_action"},

        {"name": "price_action"},

        {"name": "fibonacci"},

    ]

    duplicate = detect_duplicate(
        results
    )

    assert duplicate == [
        "price_action"
    ]


def test_remove_duplicate():

    results = [

        {"name": "price_action"},

        {"name": "price_action"},

        {"name": "fibonacci"},

    ]

    cleaned = remove_duplicate(
        results
    )

    assert len(cleaned) == 2

    assert cleaned[0]["name"] == "price_action"

    assert cleaned[1]["name"] == "fibonacci"