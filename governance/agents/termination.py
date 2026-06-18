from typing import Any

from governance.contracts import api_operation


TERMINATION_STAGES = [
    "Termination Request",
    "Biz Assessment",
    "Legal Contract Check",
    "FA Debt / Payment Check",
    "OPS Settlement Check",
    "Compliance Risk Check",
    "Data Retention / Deletion Check",
    "Final Approval",
    "Archive",
]


def build_termination_plan(ticket: dict[str, Any]) -> dict[str, Any] | None:
    if ticket.get("ticket_type") not in {"Termination", "Suspension"}:
        return None

    termination_id = ticket.get("termination_id") or f"TRM-{ticket.get('ticket_id', 'TCK-DRAFT')}"
    return {
        "termination_id": termination_id,
        "status": "Planned",
        "stages": TERMINATION_STAGES,
        "folder": "07_Termination",
        "closed_partner_target": "03_Closed_Partners",
        "operations": [
            api_operation(
                "POST",
                "/api/termination/workflows/create",
                {
                    "termination_id": termination_id,
                    "ticket_id": ticket.get("ticket_id"),
                    "stages": TERMINATION_STAGES,
                },
            ),
            api_operation(
                "POST",
                "/api/sharepoint/folders/create",
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "paths": ["07_Termination"],
                },
            ),
        ],
    }
