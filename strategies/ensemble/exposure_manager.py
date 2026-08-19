"""
==========================================
SULTAN QUANT OS
Exposure Manager
Version : 1.0.0
==========================================

Responsibilities

- Detect duplicate exposure
- Reduce duplicated strategy
- Build diversified portfolio

"""


def detect_duplicate(results):

    duplicate = []

    names = set()

    for item in results:

        name = item.get(
            "name",
            "",
        )

        if name in names:

            duplicate.append(name)

        else:

            names.add(name)

    return duplicate


def remove_duplicate(results):

    filtered = []

    names = set()

    for item in results:

        name = item.get(
            "name",
            "",
        )

        if name in names:
            continue

        names.add(name)

        filtered.append(item)

    return filtered