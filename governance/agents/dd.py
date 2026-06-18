from typing import Any


PASSING_DD_STATUSES = {"Pass", "Conditional Pass"}


def evaluate_dd_gate(ticket: dict[str, Any]) -> dict[str, Any]:
    dd_status = ticket.get("dd_status", "Pending")
    exception = ticket.get("exception") or {}
    has_exception = bool(exception.get("approved_by") and exception.get("exception_reason"))
    allowed = dd_status in PASSING_DD_STATUSES or has_exception
    return {
        "dd_status": dd_status,
        "contract_review_allowed": allowed,
        "gate_rule": 'IF dd_status NOT IN ["Pass", "Conditional Pass"] THEN block contract_review_start',
        "exception_applied": has_exception,
        "exception": exception if has_exception else None,
        "block_reason": None if allowed else "DD is not Pass or Conditional Pass.",
    }
