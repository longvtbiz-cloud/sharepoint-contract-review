from typing import Any

from governance.contracts import api_operation


def build_partner_portal_plan(ticket: dict[str, Any]) -> dict[str, Any] | None:
    if ticket.get("ticket_type") != "Partner Request" and ticket.get("role") != "EXTERNAL_PARTNER":
        return None

    request_id = ticket.get("partner_request_id") or f"PRQ-{ticket.get('ticket_id', 'TCK-DRAFT')}"
    return {
        "request_id": request_id,
        "status": "Pending Biz Preliminary Assessment",
        "visible_status": "Submitted",
        "allowed_partner_actions": [
            "upload_document",
            "submit_request",
            "submit_redline",
            "send_question",
            "view_limited_status",
        ],
        "biz_gate": {
            "stage": "Biz Preliminary Assessment",
            "decisions": ["Approve", "Reject", "Need More Info"],
            "route_if_approved": ["Legal", "Compliance", "FA", "OPS"],
        },
        "operations": [
            api_operation(
                "POST",
                "/api/partner-portal/requests",
                {
                    "request_id": request_id,
                    "ticket_id": ticket.get("ticket_id"),
                    "partner_name": ticket.get("partner_name"),
                    "submitted_by": ticket.get("created_by"),
                },
            )
        ],
    }
