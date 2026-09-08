"""
==========================================
SULTAN QUANT OS
Portfolio State Engine
Version : 1.1.1
==========================================

Responsibilities:

- Manage portfolio lifecycle state
- Provide stable portfolio state contract
- Support backward compatible state transitions
- Track state history
- Prevent invalid state transitions
- Preserve input portfolio data
- Provide safe fallback behaviour
- Support governance lifecycle state

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
    +---- decision failure ------> BLOCKED
    |
    +---- backward compatibility -> APPROVED
    |
    v
GOVERNING
    |
    +---- governance failure ----> BLOCKED
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

WARNING
    |
    +---- recovered -------------> ACTIVE
    |
    +---- rebalance -------------> REBALANCING
    |
    +---- failure ---------------> BLOCKED

REBALANCING
    |
    +---- completed -------------> ACTIVE
    |
    +---- warning ---------------> WARNING
    |
    +---- failure ---------------> BLOCKED

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

VERSION = "1.1.1"


# ==========================================================
# PORTFOLIO STATES
# ==========================================================

STATE_NEW = "NEW"

STATE_VALIDATING = "VALIDATING"

STATE_VALIDATED = "VALIDATED"

STATE_RISK_CHECK = "RISK_CHECK"

STATE_DECISION_CHECK = "DECISION_CHECK"

STATE_GOVERNING = "GOVERNING"

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

        # New governance lifecycle.
        STATE_GOVERNING,

        # Backward compatibility.
        STATE_APPROVED,

        STATE_BLOCKED,
    },

    STATE_GOVERNING: {
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

def _safe_portfolio(
    portfolio: Any,
) -> Dict[str, Any]:
    """
    Return a safe independent portfolio copy.

    Non-dictionary inputs are converted into
    an empty dictionary.
    """

    if not isinstance(
        portfolio,
        dict,
    ):
        return {}

    try:

        return deepcopy(
            portfolio
        )

    except Exception:

        return dict(
            portfolio
        )


def _safe_history(
    history: Any,
) -> List[Dict[str, Any]]:
    """
    Return a safe independent history list.
    """

    if not isinstance(
        history,
        list,
    ):
        return []

    safe_history: List[
        Dict[str, Any]
    ] = []

    for item in history:

        if isinstance(
            item,
            dict,
        ):

            try:

                safe_history.append(
                    deepcopy(
                        item
                    )
                )

            except Exception:

                safe_history.append(
                    dict(
                        item
                    )
                )

    return safe_history


def _is_known_state(
    state: Any,
) -> bool:
    """
    Check whether a state exists in
    the transition map.
    """

    return (
        isinstance(
            state,
            str,
        )
        and state in STATE_TRANSITIONS
    )


def _is_valid_transition(
    current_state: Any,
    next_state: Any,
) -> bool:
    """
    Check whether a transition is allowed.
    """

    if not _is_known_state(
        current_state
    ):
        return False

    if not _is_known_state(
        next_state
    ):
        return False

    allowed_states = (
        STATE_TRANSITIONS.get(
            current_state,
            set(),
        )
    )

    return (
        next_state
        in allowed_states
    )


def _history_entry(
    previous_state: str,
    state: str,
) -> Dict[str, str]:
    """
    Create a stable history entry.
    """

    return {

        "previous_state":
            previous_state,

        "state":
            state,

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
    """

    safe_portfolio = _safe_portfolio(
        portfolio
    )

    if not _is_known_state(
        state
    ):

        state = STATE_NEW

    return {

        "portfolio":
            safe_portfolio,

        "state":
            state,

        "previous_state":
            None,

        "history":
            [],

        "is_terminal":
            state in TERMINAL_STATES,

        "is_valid_transition":
            True,

    }


def transition_portfolio_state(
    state_result: Any,
    next_state: str,
) -> Dict[str, Any]:
    """
    Transition portfolio lifecycle state.

    Invalid transitions do not modify
    the current state.

    The returned result always follows
    the stable contract.
    """

    if not isinstance(
        state_result,
        dict,
    ):

        current_result = (
            create_portfolio_state()
        )

        current_result[
            "is_valid_transition"
        ] = False

        return current_result

    portfolio = _safe_portfolio(
        state_result.get(
            "portfolio"
        )
    )

    current_state = (
        state_result.get(
            "state",
            STATE_NEW,
        )
    )

    previous_state = (
        state_result.get(
            "previous_state"
        )
    )

    history = _safe_history(
        state_result.get(
            "history"
        )
    )

    if not _is_known_state(
        current_state
    ):

        current_state = STATE_NEW

    if not _is_known_state(
        next_state
    ):

        return {

            "portfolio":
                portfolio,

            "state":
                current_state,

            "previous_state":
                previous_state,

            "history":
                history,

            "is_terminal":
                current_state
                in TERMINAL_STATES,

            "is_valid_transition":
                False,

        }

    if not _is_valid_transition(
        current_state,
        next_state,
    ):

        return {

            "portfolio":
                portfolio,

            "state":
                current_state,

            "previous_state":
                previous_state,

            "history":
                history,

            "is_terminal":
                current_state
                in TERMINAL_STATES,

            "is_valid_transition":
                False,

        }

    updated_history = (
        history
        + [
            _history_entry(
                previous_state=current_state,
                state=next_state,
            )
        ]
    )

    return {

        "portfolio":
            portfolio,

        "state":
            next_state,

        "previous_state":
            current_state,

        "history":
            updated_history,

        "is_terminal":
            next_state
            in TERMINAL_STATES,

        "is_valid_transition":
            True,

    }


def can_transition(
    current_state: Any,
    next_state: Any,
) -> bool:
    """
    Public helper for checking whether
    a transition is valid.
    """

    return _is_valid_transition(
        current_state,
        next_state,
    )


def is_terminal_state(
    state: Any,
) -> bool:
    """
    Check whether a lifecycle state
    is terminal.
    """

    return (
        state
        in TERMINAL_STATES
    )


def get_available_transitions(
    state: Any,
) -> List[str]:
    """
    Return allowed next states.

    Unknown states return an empty list.
    """

    if not _is_known_state(
        state
    ):

        return []

    return sorted(
        STATE_TRANSITIONS.get(
            state,
            set(),
        )
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


def start_governing(
    state_result: Any,
) -> Dict[str, Any]:
    """
    DECISION_CHECK -> GOVERNING

    New governance lifecycle path.
    """

    return transition_portfolio_state(
        state_result,
        STATE_GOVERNING,
    )


def governance_passed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    GOVERNING -> APPROVED
    """

    return transition_portfolio_state(
        state_result,
        STATE_APPROVED,
    )


def governance_failed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    GOVERNING -> BLOCKED
    """

    return transition_portfolio_state(
        state_result,
        STATE_BLOCKED,
    )


def decision_passed(
    state_result: Any,
) -> Dict[str, Any]:
    """
    Backward compatible convenience path.

    DECISION_CHECK -> APPROVED

    Existing lifecycle users expect a
    successful decision to immediately
    approve the portfolio.

    New governance-aware flows should use:

        start_governing()
        governance_passed()
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


def approve_portfolio(
    state_result: Any,
) -> Dict[str, Any]:
    """
    GOVERNING -> APPROVED.

    Backward compatibility is also supported
    for DECISION_CHECK -> APPROVED.
    """

    return transition_portfolio_state(
        state_result,
        STATE_APPROVED,
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
    Transition portfolio to BLOCKED
    when allowed.
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


# ==========================================================
# PUBLIC API
# ==========================================================

__all__ = [

    "VERSION",

    "STATE_NEW",
    "STATE_VALIDATING",
    "STATE_VALIDATED",
    "STATE_RISK_CHECK",
    "STATE_DECISION_CHECK",
    "STATE_GOVERNING",
    "STATE_APPROVED",
    "STATE_ACTIVE",
    "STATE_WARNING",
    "STATE_REBALANCING",
    "STATE_BLOCKED",
    "STATE_REJECTED",

    "TERMINAL_STATES",

    "REQUIRED_STATE_KEYS",

    "STATE_TRANSITIONS",

    "required_state_keys",

    "create_portfolio_state",
    "transition_portfolio_state",

    "can_transition",

    "is_terminal_state",

    "get_available_transitions",

    "start_validation",

    "validation_passed",

    "validation_failed",

    "start_risk_check",

    "risk_passed",

    "risk_failed",

    "start_governing",

    "governance_passed",

    "governance_failed",

    "decision_passed",

    "decision_failed",

    "approve_portfolio",

    "activate_portfolio",

    "set_warning",

    "start_rebalancing",

    "rebalancing_completed",

    "block_portfolio",

    "create_state",

    "transition_state",

    "initialize_portfolio_state",

]