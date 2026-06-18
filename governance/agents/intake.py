from datetime import datetime, timezone
from typing import Any


DEFAULT_TICKET_TYPE = "New Cooperation"


def normalize_ticket(payload: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    ticket_id = payload.get("ticket_id") or "TCK-DRAFT"
    return {
        "ticket_id": ticket_id,
        "ticket_type": payload.get("ticket_type", DEFAULT_TICKET_TYPE),
        "partner_name": payload.get("partner_name", ""),
        "tax_code": payload.get("tax_code", ""),
        "project_case": payload.get("project_case", ""),
        "biz_owner": payload.get("biz_owner") or payload.get("created_by", ""),
        "priority": payload.get("priority", "Normal"),
        "due_date": payload.get("due_date", ""),
        "status": payload.get("status", "Draft"),
        "dd_status": payload.get("dd_status", "Pending"),
        "contract_review_status": payload.get("contract_review_status", "Not Started"),
        "current_round": int(payload.get("current_round", 0)),
        "action": payload.get("action", "ticket.create"),
        "sharepoint_folder_url": payload.get("sharepoint_folder_url", ""),
        "created_by": payload.get("created_by", "system"),
        "created_at": payload.get("created_at", now),
        "updated_at": now,
        "contract_type": payload.get("contract_type", ""),
        "selected_departments": payload.get("selected_departments", []),
        "contract_signals": payload.get("contract_signals", []),
        "dd_findings": payload.get("dd_findings", []),
        "dd_sources": payload.get("dd_sources", []),
        "official_file_url": payload.get("official_file_url", ""),
        "received_file_url": payload.get("received_file_url", ""),
        "negotiation_round": payload.get("negotiation_round", 1),
        "negotiation_decision": payload.get("negotiation_decision", ""),
        "key_changes": payload.get("key_changes", []),
        "open_issues": payload.get("open_issues", []),
        "partner_request_id": payload.get("partner_request_id", ""),
        "role": payload.get("role", ""),
        "termination_id": payload.get("termination_id", ""),
        "exception": payload.get("exception"),
    }
