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

CONTRACT_REVIEW_API_CONTRACTS = {
    "create_round": "POST /api/contracts/rounds/create",
    "assign_reviewers": "POST /api/contracts/rounds/{round_id}/assign-reviewers",
    "complete_review": "POST /api/contracts/rounds/{round_id}/complete-review",
    "submit_summary": "POST /api/contracts/rounds/{round_id}/submit-summary",
    "get_round": "GET /api/contracts/rounds/{round_id}",
    "list_ticket_rounds": "GET /api/contracts/tickets/{ticket_id}/rounds",
}

AI_API_CONTRACTS = {
    "dd_analyze": "POST /api/ai/dd/analyze",
    "contract_summarize": "POST /api/ai/contracts/summarize",
    "contract_compare": "POST /api/ai/contracts/compare",
    "recommend_reviewers": "POST /api/ai/contracts/recommend-reviewers",
    "contract_risk_score": "POST /api/ai/contracts/risk-score",
    "negotiation_playbook": "POST /api/ai/negotiation/playbook",
}


def all_api_contracts() -> dict[str, Any]:
    return {
        "admin": ADMIN_API_CONTRACTS,
        "sharepoint": SHAREPOINT_API_CONTRACTS,
        "dd": DD_API_CONTRACTS,
        "contract_review": CONTRACT_REVIEW_API_CONTRACTS,
        "ai": AI_API_CONTRACTS,
    }
