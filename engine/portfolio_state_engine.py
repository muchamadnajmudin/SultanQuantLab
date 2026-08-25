"""
==========================================
SULTAN QUANT OS
Portfolio State Engine
Version : 1.0.0
==========================================

Responsibilities:

- Manage portfolio lifecycle state
- Provide stable portfolio state contract
- Support backward compatible state transitions
- Track state history
- Prevent invalid state transitions
- Preserve input portfolio data
- Provide safe fallback behaviour

This module does NOT replace:

- portfolio_engine.py
- institutional_portfolio_engine.py
- institutional_engine.py
- portfolio_validation_engine.py
- portfolio_governance_engine.py
- risk/portfolio_risk.py
- decision_engine.py

The Portfolio State Engine is an independent lifecycle layer.

Lifecycle:

NEW
    |
    v
VALIDATING
    |
    +---- validation failure ----> REJECTED
    |
    v
VALIDATED
    |
    v
RISK_CHECK
    |
    +---- risk failure ----------> BLOCKED
    |
    v
DECISION_CHECK
    |
    +---- decision rejection ----> BLOCKED
    |
    v
APPROVED
    |
    v
ACTIVE
    |
    +---- warning ---------------> WARNING
    |
    +---- rebalance -------------> REBALANCING
    |
    +---- governance failure ----> BLOCKED

The engine intentionally has no dependency on live trading,
portfolio governance implementation details, or strategy engines.

Backward compatibility principle:

- Existing modules are not modified.
- Existing function signatures are not changed.
- Input objects are never modified.
- Output contract remains stable.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


# ==========================================================
# VERSION
# ==========================================================

VERSION = "1.0.0"


# ==========================================================
# PORTFOLIO STATES
# ==========================================================

STATE_NEW = "NEW"

STATE_VALIDATING = "VALIDATING"
STATE_VALIDATED = "VALIDATED"

STATE_RISK_CHECK = "RISK_CHECK"

STATE_DECISION_CHECK = "DECISION_CHECK"

STATE_APPROVED = "APPROVED"

STATE_ACTIVE = "ACTIVE"

STATE_WARNING = "WARNING"

STATE_REBALANCING = "REBALANCING"

STATE_BLOCKED = "BLOCKED"

STATE_REJECTED = "REJECTED"


# ==========================================================
# TERMINAL STATES
# ==========================================================

TERMINAL_STATES = {
    STATE_BLOCKED,
    STATE_REJECTED,
}


# ==========================================================
# REQUIRED CONTRACT KEYS
# ==========================================================

REQUIRED_STATE_KEYS = (
    "portfolio",
    "state",
    "previous_state",
    "history",
    "is_terminal",
    "is_valid_transition",
)


# ==========================================================
# STATE TRANSITIONS
# ==========================================================

STATE_TRANSITIONS = {
    STATE_NEW: {
        STATE_VALIDATING,
    },

    STATE_VALIDATING: {
        STATE_VALIDATED,
        STATE_REJECTED,
    },

    STATE_VALIDATED: {
        STATE_RISK_CHECK,
        STATE_BLOCKED,
    },

    STATE_RISK_CHECK: {
        STATE_DECISION_CHECK,
        STATE_BLOCKED,
    },

    STATE_DECISION_CHECK: {
        STATE_APPROVED,
        STATE_BLOCKED,
    },

    STATE_APPROVED: {
        STATE_ACTIVE,
        STATE_WARNING,
        STATE_REBALANCING,
        STATE_BLOCKED,
    },

    STATE_ACTIVE: {
        STATE_WARNING,
        STATE_REBALANCING,
        STATE_BLOCKED,
    },

    STATE_WARNING: {
        STATE_ACTIVE,
        STATE_REBALANCING,
        STATE_BLOCKED,
    },

    STATE_REBALANCING: {
        STATE_ACTIVE,
        STATE_WARNING,
        STATE_BLOCKED,
    },

    STATE_BLOCKED: set(),

    STATE_REJECTED: set(),
}


# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _safe_portfolio(portfolio: Any) -> Dict[str, Any]:
    """
    Return a safe independent portfolio copy.

    Non-dictionary inputs are converted into an empty dictionary.
    """

    if not isinstance(portfolio, dict):
        return {}

    return deepcopy(portfolio)


def _safe_history(history: Any) -> List[Dict[str, Any]]:
    """
    Return a safe independent history list.
    """

    if not isinstance(history, list):
        return []

    safe_history: List[Dict[str, Any]] = []

    for item in history:
        if isinstance(item, dict):
            safe_history.append(deepcopy(item))

    return safe_history


def _is_known_state(state: Any) -> bool:
    """
    Check whether a state exists in the transition map.
    """

    return isinstance(state, str) and state in STATE_TRANSITIONS


def _is_valid_transition(
    current_state: Any,
    next_state: Any,
) -> bool:
    """
    Check whether a transition is allowed.

    Unknown states are always invalid.
    """

    if not _is_known_state(current_state):
        return False

    if not _is_known_state(next_state):
        return False

    allowed_states = STATE_TRANSITIONS.get(current_state, set())

    return next_state in allowed_states


def _history_entry(
    previous_state: str,
    state: str,
) -> Dict[str, str]:
    """
    Create a stable history entry.
    """

    return {
        "previous_state": previous_state,
        "state": state,
    }


# ==========================================================
# PUBLIC CONTRACT
# ==========================================================

def required_state_keys() -> tuple:
    """
    Return the required stable state contract keys.
    """

    return REQUIRED_STATE_KEYS


def create_portfolio_state(
    portfolio: Any = None,
    state: str = STATE_NEW,
) -> Dict[str, Any]:
    """
    Create a new portfolio lifecycle state.

    Unknown input states safely fall back to NEW.

    Parameters
    ----------
    portfolio:
        Portfolio dictionary.

    state:
        Initial lifecycle state.

    Returns
    -------
    dict
        Stable portfolio state contract.
    """

    safe_portfolio = _safe_portfolio(portfolio)

    if not _is_known_state(state):
        state = STATE_NEW

    return {
        "portfolio": safe_portfolio,
        "state": state,
        "previous_state": None,
        "history": [],
        "is_terminal": state in TERMINAL_STATES,
        "is_valid_transition": True,
    }


def transition_portfolio_state(
    state_result: Any,
    next_state: str,
) -> Dict[str, Any]:
    """
    Transition portfolio lifecycle state.

    Invalid transitions do not modify the current state.

    The returned result always follows the stable contract.

    Parameters
    ----------
    state_result:
        Existing portfolio state result.

    next_state:
        Target lifecycle state.

    Returns
    -------
    dict
        Updated state contract.
    """

    if not isinstance(state_result, dict):
        current_result = create_portfolio_state()
        current_result["is_valid_transition"] = False
        return current_result

    portfolio = _safe_portfolio(
        state_result.get("portfolio")
    )

    current_state = state_result.get(
        "state",
        STATE_NEW,
    )

    previous_state = state_result.get(
        "previous_state"
    )

    history = _safe_history(
        state_result.get("history")
    )

    if not _is_known_state(current_state):
        current_state = STATE_NEW

    if not _is_known_state(next_state):
        return {
            "portfolio": portfolio,
            "state": current_state,
            "previous_state": previous_state,
            "history": history,
            "is_terminal": current_state in TERMINAL_STATES,
            "is_valid_transition": False,
        }

    if not _is_valid_transition(
        current_state,
        next_state,
    ):
        return {
            "portfolio": portfolio,
            "state": current_state,
            "previous_state": previous_state,
            "history": history,
            "is_terminal": current_state in TERMINAL_STATES,
            "is_valid_transition": False,
        }

    updated_history = history + [
        _history_entry(
            previous_state=current_state,
            state=next_state,
        )
    ]

    return {
        "portfolio": portfolio,
        "state": next_state,
        "previous_state": current_state,
        "history": updated_history,
        "is_terminal": next_state in TERMINAL_STATES,
        "is_valid_transition": True,
    }


def can_transition(
    current_state: Any,
    next_state: Any,
) -> bool:
    """
    Public helper for checking whether a transition is valid.
    """

    return _is_valid_transition(
        current_state,
        next_state,
    )


def is_terminal_state(
    state: Any,
) -> bool:
    """
    Check whether a lifecycle state is terminal.
    """

    return state in TERMINAL_STATES


def get_available_transitions(
    state: Any,
) -> List[str]:
    """
    Return allowed next states.

    Unknown states return an empty list.
    """

    if not _is_known_state(state):
        return []

    return sorted(
        STATE_TRANSITIONS.get(state, set())
    )


# ==========================================================
# CONVENIENCE TRANSITIONS
# ==========================================================

def start_validation(
    state_result: Any,
) -> Dict[str, Any]:
    """
    NEW -> VALIDATING
    """

    return transition_portfolio_state(
        state_result,
        STATE_VALIDATING,
    )


def validation_passed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    VALIDATING -> VALIDATED
    """

    return transition_portfolio_state(
        state_result,
        STATE_VALIDATED,
    )


def validation_failed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    VALIDATING -> REJECTED
    """

    return transition_portfolio_state(
        state_result,
        STATE_REJECTED,
    )


def start_risk_check(
    state_result: Any,
) -> Dict[str, Any]:
    """
    VALIDATED -> RISK_CHECK
    """

    return transition_portfolio_state(
        state_result,
        STATE_RISK_CHECK,
    )


def risk_passed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    RISK_CHECK -> DECISION_CHECK
    """

    return transition_portfolio_state(
        state_result,
        STATE_DECISION_CHECK,
    )


def risk_failed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    RISK_CHECK -> BLOCKED
    """

    return transition_portfolio_state(
        state_result,
        STATE_BLOCKED,
    )


def decision_passed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    DECISION_CHECK -> APPROVED
    """

    return transition_portfolio_state(
        state_result,
        STATE_APPROVED,
    )


def decision_failed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    DECISION_CHECK -> BLOCKED
    """

    return transition_portfolio_state(
        state_result,
        STATE_BLOCKED,
    )


def activate_portfolio(
    state_result: Any,
) -> Dict[str, Any]:
    """
    APPROVED -> ACTIVE
    """

    return transition_portfolio_state(
        state_result,
        STATE_ACTIVE,
    )


def set_warning(
    state_result: Any,
) -> Dict[str, Any]:
    """
    ACTIVE/APPROVED/REBALANCING -> WARNING
    """

    return transition_portfolio_state(
        state_result,
        STATE_WARNING,
    )


def start_rebalancing(
    state_result: Any,
) -> Dict[str, Any]:
    """
    ACTIVE/WARNING/APPROVED -> REBALANCING
    """

    return transition_portfolio_state(
        state_result,
        STATE_REBALANCING,
    )


def rebalancing_completed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    REBALANCING -> ACTIVE
    """

    return transition_portfolio_state(
        state_result,
        STATE_ACTIVE,
    )


def block_portfolio(
    state_result: Any,
) -> Dict[str, Any]:
    """
    Transition the portfolio to BLOCKED when allowed.
    """

    return transition_portfolio_state(
        state_result,
        STATE_BLOCKED,
    )


# ==========================================================
# BACKWARD COMPATIBLE ALIASES
# ==========================================================

def create_state(
    portfolio: Any = None,
    state: str = STATE_NEW,
) -> Dict[str, Any]:
    """
    Backward compatible alias.
    """

    return create_portfolio_state(
        portfolio=portfolio,
        state=state,
    )


def transition_state(
    state_result: Any,
    next_state: str,
) -> Dict[str, Any]:
    """
    Backward compatible alias.
    """

    return transition_portfolio_state(
        state_result=state_result,
        next_state=next_state,
    )


def initialize_portfolio_state(
    portfolio: Any = None,
) -> Dict[str, Any]:
    """
    Convenience initializer.

    Always starts at NEW.
    """

    return create_portfolio_state(
        portfolio=portfolio,
        state=STATE_NEW,
    )