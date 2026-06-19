from typing import Any


def build_dashboard_snapshot(
    ticket: dict[str, Any],
    dd_result: dict[str, Any] | None,
    review_plan: dict[str, Any] | None,
    negotiation_plan: dict[str, Any] | None,
    partner_portal_plan: dict[str, Any] | None,
    termination_plan: dict[str, Any] | None,
    audit_events: list[dict[str, Any]],
    workflow_status: str,
) -> dict[str, Any]:
    dd_status = (dd_result or {}).get("dd_status", ticket.get("dd_status", "Pending"))
    review_status = (review_plan or {}).get("status", ticket.get("contract_review_status", "Not Started"))
    risk_level = (dd_result or {}).get("risk_level", "Unknown")

    counters = {
        "open_tickets": 0 if ticket.get("status") in {"Closed", "Archived"} else 1,
        "pending_dd": 1 if dd_status in {"Pending", "In Review", "Need More Info"} else 0,
        "dd_rejected": 1 if dd_status == "Reject" else 0,
        "dd_conditional_pass": 1 if dd_status == "Conditional Pass" else 0,
        "contracts_in_review": 1 if review_status in {"Ready", "Pending Review", "In Review"} else 0,
        "overdue_review": 0,
        "negotiation_rounds_open": 1 if negotiation_plan else 0,
        "high_risk_partners": 1 if risk_level in {"High", "Critical"} else 0,
        "partner_requests_pending_biz_approval": 1 if partner_portal_plan else 0,
        "termination_pending": 1 if termination_plan else 0,
        "signed_contracts_this_month": 0,
    }

    review_tasks = (review_plan or {}).get("reviewer_tasks", [])
    reviews_by_department = {}
    for task in review_tasks:
        department = task.get("department", "Unknown")
        reviews_by_department[department] = reviews_by_department.get(department, 0) + 1

    return {
        "ticket_id": ticket.get("ticket_id"),
        "workflow_status": workflow_status,
        "counters": counters,
        "reviews_by_department": reviews_by_department,
        "queues": {
            "dd": dd_status,
            "contract_review": review_status,
            "partner_request": (partner_portal_plan or {}).get("status"),
            "termination": (termination_plan or {}).get("status"),
        },
        "risk": {
            "level": risk_level,
            "matched_rules": (dd_result or {}).get("matched_rules", []),
        },
        "audit_event_count": len(audit_events),
    }
