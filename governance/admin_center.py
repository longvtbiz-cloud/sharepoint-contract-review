from typing import Any

from governance.agents.office365 import GRAPH_SCOPES
from governance.agents.rbac import DEFAULT_ROLES
from governance.dd_rulebook import DD_DATA_SOURCE_CATALOG
from governance.review_matrix import CONTRACT_TYPE_MATRIX


DEFAULT_DEPARTMENTS = [
    "Legal",
    "Compliance",
    "FA",
    "OPS",
    "Risk",
    "AML",
    "PDPA",
    "Security",
    "Product",
    "IT",
    "Tax",
    "Procurement",
]


def build_governance_catalog() -> dict[str, Any]:
    return {
        "roles": sorted(DEFAULT_ROLES),
        "departments": DEFAULT_DEPARTMENTS,
        "review_matrix": CONTRACT_TYPE_MATRIX,
        "dd_data_sources": DD_DATA_SOURCE_CATALOG,
        "office365_connector": {
            "provider": "Microsoft Graph",
            "scopes": GRAPH_SCOPES,
            "status": "inactive_until_configured",
        },
        "sharepoint_mapping": {
            "root": "Partner Cooperation Management",
            "ticket_library": "02_Cooperation_Tickets",
            "audit_folder": "99_Audit_Trail",
        },
        "override_policy": {
            "allowed_roles": ["LEGAL_ADMIN"],
            "requires_reason": True,
            "requires_risk_acceptance": True,
            "audit_action": "workflow.override_approved",
        },
    }
