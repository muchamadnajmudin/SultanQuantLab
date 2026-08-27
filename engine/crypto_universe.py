"""
==========================================
SULTAN QUANT OS
Module : Crypto Universe
Version : 1.0.0
==========================================

Crypto universe management.

Responsibilities
----------------
- Normalize crypto symbols
- Filter symbols by quote currency
- Remove invalid symbols
- Remove duplicates
- Build a clean crypto trading universe
- Support multiple data sources

Important
---------
This module does NOT:

- Connect directly to an exchange
- Fetch live market data
- Rank cryptocurrencies
- Execute trades
- Modify existing Grid modules

It only manages the list of candidate symbols.

Example
-------

symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "HYPEUSDT",
]

universe = CryptoUniverse.from_symbols(
    symbols,
    quote="USDT",
)

print(universe.symbols)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


# ============================================================
# DATA MODEL
# ============================================================


@dataclass(frozen=True)
class CryptoUniverseResult:
    """
    Result of crypto universe construction.
    """

    symbols: list[str]

    quote: str

    total_input: int

    total_valid: int

    total_removed: int

    def to_dict(self) -> dict:
        return {
            "symbols": self.symbols.copy(),
            "quote": self.quote,
            "total_input": self.total_input,
            "total_valid": self.total_valid,
            "total_removed": self.total_removed,
        }


# ============================================================
# CRYPTO UNIVERSE
# ============================================================


class CryptoUniverse:
    """
    Manage a clean list of crypto trading symbols.

    The class is intentionally exchange-independent.

    Example
    -------

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
        ],
        quote="USDT",
    )
    """

    def __init__(
        self,
        symbols: Iterable[str],
        quote: str = "USDT",
    ):
        self.quote = self._normalize_quote(
            quote
        )

        self._input_symbols = list(
            symbols
        )

        self.symbols = self._build_universe(
            self._input_symbols
        )

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize_quote(
        quote: str,
    ) -> str:
        """
        Normalize quote currency.
        """

        if not isinstance(
            quote,
            str,
        ):
            raise TypeError(
                "quote must be a string"
            )

        result = quote.strip().upper()

        if not result:
            raise ValueError(
                "quote must not be empty"
            )

        return result

    @staticmethod
    def normalize_symbol(
        symbol: str,
    ) -> str:
        """
        Normalize a crypto symbol.

        Examples
        --------

        btcusdt
            -> BTCUSDT

        BTC/USDT
            -> BTCUSDT

        BTC-USDT
            -> BTCUSDT

        BTC_USDT
            -> BTCUSDT

        BTC USDT
            -> BTCUSDT
        """

        if not isinstance(
            symbol,
            str,
        ):
            raise TypeError(
                "symbol must be a string"
            )

        result = (
            symbol
            .strip()
            .upper()
        )

        if not result:
            raise ValueError(
                "symbol must not be empty"
            )

        for separator in (
            "/",
            "-",
            "_",
            " ",
        ):
            result = result.replace(
                separator,
                "",
            )

        if not result:
            raise ValueError(
                "symbol must not be empty"
            )

        return result

    # ========================================================
    # VALIDATION
    # ========================================================

    def is_valid_symbol(
        self,
        symbol: str,
    ) -> bool:
        """
        Check whether a symbol belongs to
        the configured quote currency.

        Example
        -------

        quote = USDT

        BTCUSDT -> True
        ETHUSDT -> True
        BTCUSD  -> False
        """

        normalized = self.normalize_symbol(
            symbol
        )

        if len(normalized) <= len(
            self.quote
        ):
            return False

        return normalized.endswith(
            self.quote
        )

    # ========================================================
    # UNIVERSE BUILDER
    # ========================================================

    def _build_universe(
        self,
        symbols: Iterable[str],
    ) -> list[str]:
        """
        Build a clean and unique symbol universe.
        """

        result = []

        seen = set()

        for symbol in symbols:

            try:

                normalized = (
                    self.normalize_symbol(
                        symbol
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            if not self.is_valid_symbol(
                normalized
            ):
                continue

            if normalized in seen:
                continue

            seen.add(
                normalized
            )

            result.append(
                normalized
            )

        return result

    # ========================================================
    # RESULT
    # ========================================================

    def result(
        self,
    ) -> CryptoUniverseResult:
        """
        Return the current universe result.
        """

        total_input = len(
            self._input_symbols
        )

        total_valid = len(
            self.symbols
        )

        total_removed = (
            total_input
            - total_valid
        )

        return CryptoUniverseResult(
            symbols=self.symbols.copy(),
            quote=self.quote,
            total_input=total_input,
            total_valid=total_valid,
            total_removed=total_removed,
        )

    # ========================================================
    # CONVENIENCE CONSTRUCTOR
    # ========================================================

    @classmethod
    def from_symbols(
        cls,
        symbols: Iterable[str],
        quote: str = "USDT",
    ) -> "CryptoUniverse":
        """
        Create a universe directly from symbols.
        """

        return cls(
            symbols=symbols,
            quote=quote,
        )

    # ========================================================
    # BASIC CONTAINER METHODS
    # ========================================================

    def __len__(
        self,
    ) -> int:
        return len(
            self.symbols
        )

    def __contains__(
        self,
        symbol: str,
    ) -> bool:
        try:

            normalized = (
                self.normalize_symbol(
                    symbol
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            return False

        return normalized in self.symbols

    def __iter__(
        self,
    ):
        return iter(
            self.symbols
        )

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}("
            f"symbols={len(self.symbols)}, "
            f"quote='{self.quote}'"
            f")"
        )