from typing import Any


LEGAL_ADMIN = "LEGAL_ADMIN"
EXTERNAL_PARTNER = "EXTERNAL_PARTNER"

DEFAULT_ROLES = {
    "LEGAL_ADMIN",
    "LEGAL_MANAGER",
    "LEGAL_REVIEWER",
    "COMPLIANCE_MANAGER",
    "COMPLIANCE_REVIEWER",
    "DD_MANAGER",
    "DD_REVIEWER",
    "BIZ_MANAGER",
    "BIZ_OWNER",
    "FA_MANAGER",
    "FA_REVIEWER",
    "OPS_MANAGER",
    "OPS_REVIEWER",
    "RISK_MANAGER",
    "RISK_REVIEWER",
    "SECURITY_REVIEWER",
    "PDPA_REVIEWER",
    "PRODUCT_REVIEWER",
    "EXTERNAL_PARTNER",
    "VIEW_ONLY",
}

ACTION_ROLES = {
    "ticket.create": {"LEGAL_ADMIN", "BIZ_MANAGER", "BIZ_OWNER"},
    "ticket.view": DEFAULT_ROLES,
    "document.upload": {"LEGAL_ADMIN", "BIZ_MANAGER", "BIZ_OWNER", "EXTERNAL_PARTNER"},
    "contract.review.start": {"LEGAL_ADMIN", "BIZ_MANAGER", "BIZ_OWNER"},
    "review.complete": {
        "LEGAL_ADMIN",
        "LEGAL_REVIEWER",
        "COMPLIANCE_REVIEWER",
        "DD_REVIEWER",
        "FA_REVIEWER",
        "OPS_REVIEWER",
        "RISK_REVIEWER",
        "SECURITY_REVIEWER",
        "PDPA_REVIEWER",
        "PRODUCT_REVIEWER",
    },
    "partner.request.submit": {"EXTERNAL_PARTNER", "LEGAL_ADMIN", "BIZ_OWNER", "BIZ_MANAGER"},
    "counterparty.send": {"LEGAL_ADMIN", "BIZ_OWNER", "BIZ_MANAGER"},
    "counterparty.receive": {"LEGAL_ADMIN", "BIZ_OWNER", "BIZ_MANAGER"},
    "termination.create": {"LEGAL_ADMIN", "LEGAL_MANAGER", "BIZ_MANAGER", "BIZ_OWNER"},
    "admin.configure": {"LEGAL_ADMIN"},
    "workflow.override": {"LEGAL_ADMIN"},
}

EXTERNAL_RESTRICTED_FIELDS = {
    "dd_result",
    "review_plan",
    "audit_events",
    "internal_risk_score",
    "internal_comments",
    "legal_memo",
    "approval_notes",
    "api_contracts",
    "negotiation_plan",
    "termination_plan",
    "ai_plan",
    "dashboard_snapshot",
    "office365_plan",
}


def evaluate_access(payload: dict[str, Any], ticket: dict[str, Any]) -> dict[str, Any]:
    role = payload.get("role", "BIZ_OWNER")
    action = payload.get("action", "ticket.create")
    actor = payload.get("actor") or payload.get("created_by") or ticket.get("created_by", "system")

    if role == LEGAL_ADMIN:
        allowed = True
    else:
        allowed = role in ACTION_ROLES.get(action, set())

    denied_reason = None
    if role not in DEFAULT_ROLES:
        allowed = False
        denied_reason = f"Unknown role: {role}"
    elif not allowed:
        denied_reason = f"Role {role} is not allowed to perform {action}."

    return {
        "actor": actor,
        "role": role,
        "action": action,
        "allowed": allowed,
        "denied_reason": denied_reason,
        "visibility": "external_limited" if role == EXTERNAL_PARTNER else "internal",
        "restricted_fields": sorted(EXTERNAL_RESTRICTED_FIELDS) if role == EXTERNAL_PARTNER else [],
    }


def sanitize_response(response: dict[str, Any], access_result: dict[str, Any] | None) -> dict[str, Any]:
    if not access_result or access_result.get("visibility") != "external_limited":
        return response

    sanitized = dict(response)
    for field in EXTERNAL_RESTRICTED_FIELDS:
        sanitized.pop(field, None)
    ticket = dict(sanitized.get("ticket") or {})
    ticket.pop("sharepoint_folder_url", None)
    sanitized["ticket"] = {
        "ticket_id": ticket.get("ticket_id"),
        "ticket_type": ticket.get("ticket_type"),
        "partner_name": ticket.get("partner_name"),
        "project_case": ticket.get("project_case"),
        "status": ticket.get("status"),
        "contract_review_status": ticket.get("contract_review_status"),
    }
    sanitized["visibility"] = "external_limited"
    return sanitized
