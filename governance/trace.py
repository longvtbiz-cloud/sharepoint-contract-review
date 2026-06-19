from copy import deepcopy
from typing import Any


def _append_trace(
    trace: list[dict[str, Any]],
    gate: str,
    decision: str,
    status: str,
    reasons: list[str] | None = None,
) -> None:
    trace.append(
        {
            "sequence": len(trace) + 1,
            "gate": gate,
            "decision": decision,
            "status": status,
            "reasons": reasons or [],
        }
    )


def build_decision_trace(result: dict[str, Any]) -> list[dict[str, Any]]:
    trace: list[dict[str, Any]] = []

    access_result = result.get("access_result") or {}
    if access_result:
        allowed = bool(access_result.get("allowed"))
        _append_trace(
            trace,
            "rbac",
            "allow" if allowed else "deny",
            "passed" if allowed else "blocked",
            [] if allowed else [access_result.get("denied_reason") or "Access denied."],
        )
        if not allowed:
            return deepcopy(trace)

    policy_result = result.get("policy_result") or {}
    if policy_result:
        violations = [
            violation.get("message") or violation.get("code")
            for violation in policy_result.get("violations", [])
            if violation.get("message") or violation.get("code")
        ]
        allowed = bool(policy_result.get("allowed"))
        _append_trace(
            trace,
            "critical_policy",
            "allow" if allowed else "block",
            "passed" if allowed else "blocked",
            violations,
        )
        if not allowed:
            return deepcopy(trace)

    dd_result = result.get("dd_result") or {}
    if dd_result:
        allowed = bool(dd_result.get("contract_review_allowed"))
        reasons = []
        if not allowed:
            reasons.append(dd_result.get("reason") or "DD gate blocks contract review.")
        _append_trace(
            trace,
            "dd_gate",
            "allow_contract_review" if allowed else "block_contract_review",
            "passed" if allowed else "blocked",
            reasons,
        )

    review_plan = result.get("review_plan") or {}
    if review_plan:
        ready = review_plan.get("status") == "Ready"
        missing = review_plan.get("missing_mandatory_departments") or []
        _append_trace(
            trace,
            "review_matrix",
            "ready" if ready else "needs_reviewer_selection",
            "passed" if ready else "attention_required",
            [f"Missing mandatory departments: {', '.join(missing)}"] if missing else [],
        )

    sla_plan = result.get("sla_plan") or {}
    if sla_plan:
        _append_trace(
            trace,
            "sla",
            sla_plan.get("status", "planned"),
            "planned" if sla_plan.get("status") == "planned" else "attention_required",
            [f"SLA hours: {sla_plan.get('sla_hours')}"] if sla_plan.get("sla_hours") else [],
        )

    execution_plan = result.get("execution_plan") or {}
    if execution_plan:
        _append_trace(
            trace,
            "execution",
            execution_plan.get("mode", "dry_run"),
            execution_plan.get("status", "planned"),
            [f"Planned steps: {execution_plan.get('total_steps', 0)}"],
        )

    audit_plan = result.get("audit_plan") or {}
    if audit_plan:
        _append_trace(
            trace,
            "audit_persistence",
            audit_plan.get("status", "planned"),
            "planned",
            [f"Audit events: {audit_plan.get('event_count', 0)}"],
        )

    return deepcopy(trace)
