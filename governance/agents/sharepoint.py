from datetime import datetime
from typing import Any


def _safe_part(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.strip())
    return "_".join(part for part in cleaned.split("_") if part) or "NA"


def build_sharepoint_plan(ticket: dict[str, Any]) -> dict[str, Any]:
    date_prefix = datetime.now().strftime("%Y%m%d")
    partner = _safe_part(ticket.get("partner_name", "Partner"))
    project = _safe_part(ticket.get("project_case", "Project"))
    ticket_id = _safe_part(ticket.get("ticket_id", "TCK-DRAFT"))
    ticket_folder = f"{date_prefix}_{partner}_{project}_{ticket_id}"
    return {
        "root": "Partner Cooperation Management",
        "partner_master_folder": f"01_Partner_Master/{partner}_{_safe_part(ticket.get('tax_code', 'NA'))}",
        "ticket_folder": f"02_Cooperation_Tickets/{ticket_folder}",
        "subfolders": [
            "00_Intake",
            "01_DD",
            "02_Internal_Review/Round_01",
            "02_Internal_Review/Round_02",
            "02_Internal_Review/Round_03",
            "03_Counterparty_Negotiation/Sent",
            "03_Counterparty_Negotiation/Received",
            "04_Final",
            "05_Signed",
            "06_Post_Signing_Requests",
            "07_Termination",
            "99_Audit_Trail",
        ],
        "api_actions": [
            "POST /api/sharepoint/folders/create",
            "POST /api/sharepoint/permissions/grant",
        ],
    }
