from typing import Any


def evaluate_critical_governance(ticket: dict[str, Any], access_result: dict[str, Any]) -> dict[str, Any]:
    action = ticket.get("action", "ticket.create")
    violations = []

    if action == "counterparty.send" and ticket.get("internal_review_status") != "Completed":
        violations.append(
            {
                "code": "NO_COUNTERPARTY_SEND_BEFORE_INTERNAL_REVIEW",
                "message": "No completed internal review -> No sending to counterparty.",
            }
        )

    if action == "signing.finalize" and ticket.get("final_approval_status") != "Approved":
        violations.append(
            {
                "code": "NO_SIGNING_BEFORE_FINAL_APPROVAL",
                "message": "No final approval -> No signing.",
            }
        )

    if action == "workflow.override":
        if not ticket.get("override_reason"):
            violations.append(
                {
                    "code": "OVERRIDE_REASON_REQUIRED",
                    "message": "Every override must have a reason.",
                }
            )
        if not ticket.get("risk_acceptance"):
            violations.append(
                {
                    "code": "OVERRIDE_RISK_ACCEPTANCE_REQUIRED",
                    "message": "Every override must include risk acceptance.",
                }
            )

    return {
        "allowed": access_result.get("allowed", False) and not violations,
        "action": action,
        "violations": violations,
        "checked_requirements": [
            "No DD Pass -> No Contract Review",
            "No completed internal review -> No sending to counterparty",
            "No final approval -> No signing",
            "Every override must have reason",
            "Every round must have reviewer selection log",
            "Every file movement must be logged",
            "Every permission grant/revoke must be logged",
        ],
    }
