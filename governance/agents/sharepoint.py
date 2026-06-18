from datetime import datetime
from typing import Any

from governance.contracts import SHAREPOINT_API_CONTRACTS, api_operation


def _safe_part(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.strip())
    return "_".join(part for part in cleaned.split("_") if part) or "NA"


def build_sharepoint_plan(ticket: dict[str, Any]) -> dict[str, Any]:
    date_prefix = datetime.now().strftime("%Y%m%d")
    partner = _safe_part(ticket.get("partner_name", "Partner"))
    project = _safe_part(ticket.get("project_case", "Project"))
    ticket_id = _safe_part(ticket.get("ticket_id", "TCK-DRAFT"))
    ticket_folder = f"{date_prefix}_{partner}_{project}_{ticket_id}"
    subfolders = [
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
    ]
    ticket_folder_path = f"02_Cooperation_Tickets/{ticket_folder}"
    folder_paths = [
        f"01_Partner_Master/{partner}_{_safe_part(ticket.get('tax_code', 'NA'))}",
        ticket_folder_path,
        *[f"{ticket_folder_path}/{subfolder}" for subfolder in subfolders],
    ]
    return {
        "root": "Partner Cooperation Management",
        "partner_master_folder": f"01_Partner_Master/{partner}_{_safe_part(ticket.get('tax_code', 'NA'))}",
        "ticket_folder": ticket_folder_path,
        "subfolders": subfolders,
        "api_actions": list(SHAREPOINT_API_CONTRACTS.values()),
        "operations": [
            api_operation(
                "POST",
                "/api/sharepoint/folders/create",
                {
                    "root": "Partner Cooperation Management",
                    "paths": folder_paths,
                    "ticket_id": ticket.get("ticket_id"),
                },
            ),
            api_operation(
                "POST",
                "/api/sharepoint/permissions/grant",
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "folder": ticket_folder_path,
                    "principal": ticket.get("biz_owner") or ticket.get("created_by"),
                    "role": "contributor",
                },
            ),
        ],
    }
