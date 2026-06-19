from typing import Any


PLAN_ORDER = [
    "admin_plan",
    "dd_result",
    "review_plan",
    "sharepoint_plan",
    "negotiation_plan",
    "partner_portal_plan",
    "termination_plan",
    "ai_plan",
    "office365_plan",
]


def _extract_operations(plan_name: str, plan: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not plan:
        return []
    if plan_name == "dd_result":
        return ((plan.get("data_source_plan") or {}).get("operations") or [])
    return plan.get("operations") or []


def build_execution_plan(state: dict[str, Any]) -> dict[str, Any]:
    steps = []
    for plan_name in PLAN_ORDER:
        for operation in _extract_operations(plan_name, state.get(plan_name)):
            step_number = len(steps) + 1
            steps.append(
                {
                    "step": step_number,
                    "source_plan": plan_name,
                    "operation": operation,
                    "status": "planned",
                    "requires_audit_log": True,
                    "depends_on": [step_number - 1] if step_number > 1 else [],
                }
            )

    return {
        "status": "planned",
        "mode": "dry_run",
        "total_steps": len(steps),
        "steps": steps,
        "execution_guards": [
            "Do not execute if RBAC denied access.",
            "Do not execute if critical governance policy has violations.",
            "Every file movement must be logged.",
            "Every permission grant/revoke must be logged.",
            "No hard delete; only archive, deactivate, or supersede.",
        ],
    }
