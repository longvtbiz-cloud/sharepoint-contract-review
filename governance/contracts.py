from typing import Any


def api_operation(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "method": method,
        "path": path,
        "payload": payload or {},
        "status": "planned",
    }


ADMIN_API_CONTRACTS = {
    "users": {
        "create": "POST /api/admin/users",
        "update": "PUT /api/admin/users/{user_id}",
        "delete": "DELETE /api/admin/users/{user_id}",
    },
    "departments": {
        "create": "POST /api/admin/departments",
        "update": "PUT /api/admin/departments/{department_id}",
        "delete": "DELETE /api/admin/departments/{department_id}",
    },
    "review_matrix": {
        "create": "POST /api/admin/review-matrix",
        "update": "PUT /api/admin/review-matrix/{matrix_id}",
        "delete": "DELETE /api/admin/review-matrix/{matrix_id}",
    },
    "dd_rules": {
        "create": "POST /api/admin/dd-rules",
        "update": "PUT /api/admin/dd-rules/{rule_id}",
        "delete": "DELETE /api/admin/dd-rules/{rule_id}",
    },
    "audit_logs": {
        "list": "GET /api/admin/audit-logs",
    },
    "connectors": {
        "office365": "POST /api/admin/connectors/office365",
        "sharepoint_mapping": "POST /api/admin/sharepoint-mapping",
    },
}

SHAREPOINT_API_CONTRACTS = {
    "create_folder": "POST /api/sharepoint/folders/create",
    "upload_file": "POST /api/sharepoint/files/upload",
    "move_file": "POST /api/sharepoint/files/move",
    "copy_file": "POST /api/sharepoint/files/copy",
    "grant_permission": "POST /api/sharepoint/permissions/grant",
    "revoke_permission": "POST /api/sharepoint/permissions/revoke",
    "get_file": "GET /api/sharepoint/files/{file_id}",
    "get_ticket_folder": "GET /api/sharepoint/folders/{ticket_id}",
}

DD_API_CONTRACTS = {
    "start": "POST /api/dd/start",
    "reassess": "POST /api/dd/reassess",
    "result": "GET /api/dd/result/{ticket_id}",
    "approve": "POST /api/dd/approve",
    "reject": "POST /api/dd/reject",
    "request_more_info": "POST /api/dd/request-more-info",
}

DATA_SOURCE_API_CONTRACTS = {
    "create": "POST /api/data-sources",
    "list": "GET /api/data-sources",
    "update": "PUT /api/data-sources/{source_id}",
    "delete": "DELETE /api/data-sources/{source_id}",
    "test": "POST /api/data-sources/{source_id}/test",
    "sync": "POST /api/data-sources/{source_id}/sync",
}

CONTRACT_REVIEW_API_CONTRACTS = {
    "create_round": "POST /api/contracts/rounds/create",
    "assign_reviewers": "POST /api/contracts/rounds/{round_id}/assign-reviewers",
    "complete_review": "POST /api/contracts/rounds/{round_id}/complete-review",
    "submit_summary": "POST /api/contracts/rounds/{round_id}/submit-summary",
    "get_round": "GET /api/contracts/rounds/{round_id}",
    "list_ticket_rounds": "GET /api/contracts/tickets/{ticket_id}/rounds",
}

PARTNER_PORTAL_API_CONTRACTS = {
    "create_request": "POST /api/partner-portal/requests",
    "upload_document": "POST /api/partner-portal/documents/upload",
    "submit_redline": "POST /api/partner-portal/redlines",
    "submit_question": "POST /api/partner-portal/questions",
    "get_limited_status": "GET /api/partner-portal/tickets/{ticket_id}/status",
}

TERMINATION_API_CONTRACTS = {
    "create_workflow": "POST /api/termination/workflows/create",
    "advance_stage": "POST /api/termination/workflows/{termination_id}/advance",
    "final_approval": "POST /api/termination/workflows/{termination_id}/final-approval",
    "archive": "POST /api/termination/workflows/{termination_id}/archive",
}

AI_API_CONTRACTS = {
    "dd_analyze": "POST /api/ai/dd/analyze",
    "contract_summarize": "POST /api/ai/contracts/summarize",
    "contract_compare": "POST /api/ai/contracts/compare",
    "recommend_reviewers": "POST /api/ai/contracts/recommend-reviewers",
    "contract_risk_score": "POST /api/ai/contracts/risk-score",
    "negotiation_playbook": "POST /api/ai/negotiation/playbook",
    "termination_checklist": "POST /api/ai/termination/checklist",
}

OFFICE365_API_CONTRACTS = {
    "users": "GET /api/office365/users",
    "groups": "GET /api/office365/groups",
    "send_mail": "POST /api/office365/mail/send",
    "calendar_reminders": "POST /api/office365/calendar/reminders",
    "teams_notify": "POST /api/office365/teams/notify",
    "sharepoint_library": "GET /api/office365/sharepoint/library",
    "onedrive_reference": "GET /api/office365/onedrive/files/{file_id}",
}


def all_api_contracts() -> dict[str, Any]:
    return {
        "admin": ADMIN_API_CONTRACTS,
        "sharepoint": SHAREPOINT_API_CONTRACTS,
        "data_sources": DATA_SOURCE_API_CONTRACTS,
        "dd": DD_API_CONTRACTS,
        "contract_review": CONTRACT_REVIEW_API_CONTRACTS,
        "partner_portal": PARTNER_PORTAL_API_CONTRACTS,
        "termination": TERMINATION_API_CONTRACTS,
        "ai": AI_API_CONTRACTS,
        "office365": OFFICE365_API_CONTRACTS,
    }
