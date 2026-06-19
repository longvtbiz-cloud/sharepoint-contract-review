from typing import Any

from governance.contracts import api_operation


DEFAULT_REVIEW_SLA_HOURS = 48
HIGH_RISK_REVIEW_SLA_HOURS = 24
REMINDER_BEFORE_DUE_HOURS = 8
ESCALATION_AFTER_DUE_HOURS = 4


def _review_sla_hours(ticket: dict[str, Any]) -> int:
    risk_level = ticket.get("risk_level") or ticket.get("dd_risk_level") or "Unknown"
    priority = ticket.get("priority", "Normal")
    if risk_level in {"High", "Critical"} or priority in {"High", "Urgent"}:
        return HIGH_RISK_REVIEW_SLA_HOURS
    return DEFAULT_REVIEW_SLA_HOURS


def build_sla_plan(ticket: dict[str, Any], review_plan: dict[str, Any] | None) -> dict[str, Any]:
    if not review_plan:
        return {
            "status": "no_review_tasks",
            "ticket_id": ticket.get("ticket_id"),
            "rules": [],
            "operations": [],
        }

    reviewer_tasks = review_plan.get("reviewer_tasks", [])
    if review_plan.get("status") != "Ready":
        return {
            "status": "blocked_until_reviewer_selection_complete",
            "ticket_id": ticket.get("ticket_id"),
            "rules": [
                "SLA countdown starts only after all mandatory reviewer departments are selected.",
            ],
            "missing_mandatory_departments": review_plan.get("missing_mandatory_departments", []),
            "operations": [],
        }

    sla_hours = _review_sla_hours(ticket)
    task_ids = [task["task_id"] for task in reviewer_tasks]
    escalation_roles = sorted(
        {task.get("reviewer_role", "VIEW_ONLY").replace("_REVIEWER", "_MANAGER") for task in reviewer_tasks}
    )

    return {
        "status": "planned",
        "ticket_id": ticket.get("ticket_id"),
        "round_id": review_plan.get("round_id"),
        "sla_hours": sla_hours,
        "reminder_before_due_hours": REMINDER_BEFORE_DUE_HOURS,
        "escalation_after_due_hours": ESCALATION_AFTER_DUE_HOURS,
        "rules": [
            "Reviewer task due dates are calculated from review round creation time.",
            "Reminder is sent before the task due time.",
            "Escalation is sent to department manager roles after overdue threshold.",
            "Overdue scans never change contract files; they only create notifications and audit events.",
        ],
        "task_slas": [
            {
                "task_id": task["task_id"],
                "department": task.get("department"),
                "reviewer_role": task.get("reviewer_role"),
                "sla_hours": sla_hours,
                "status": "planned",
            }
            for task in reviewer_tasks
        ],
        "operations": [
            api_operation(
                "POST",
                "/api/sla/review-tasks/schedule-reminders",
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "round_id": review_plan.get("round_id"),
                    "task_ids": task_ids,
                    "reminder_before_due_hours": REMINDER_BEFORE_DUE_HOURS,
                },
            ),
            api_operation(
                "POST",
                "/api/sla/review-tasks/escalations",
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "round_id": review_plan.get("round_id"),
                    "task_ids": task_ids,
                    "escalation_after_due_hours": ESCALATION_AFTER_DUE_HOURS,
                    "escalation_roles": escalation_roles,
                },
            ),
            api_operation(
                "POST",
                "/api/sla/review-tasks/overdue-scan",
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "round_id": review_plan.get("round_id"),
                    "scope": "current_round",
                },
            ),
        ],
    }
