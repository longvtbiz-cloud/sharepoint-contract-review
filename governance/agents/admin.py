from typing import Any

from governance.admin_center import build_governance_catalog
from governance.contracts import api_operation


def build_admin_governance_plan(ticket: dict[str, Any], access_result: dict[str, Any]) -> dict[str, Any]:
    catalog = build_governance_catalog()
    is_legal_admin = access_result.get("role") == "LEGAL_ADMIN"
    operations = [
        api_operation("GET", "/api/admin/audit-logs", {"ticket_id": ticket.get("ticket_id")}),
    ]

    if is_legal_admin:
        operations.extend(
            [
                api_operation("POST", "/api/admin/users", {"mode": "configure"}),
                api_operation("POST", "/api/admin/departments", {"departments": catalog["departments"]}),
                api_operation("POST", "/api/admin/review-matrix", {"matrix": catalog["review_matrix"]}),
                api_operation("POST", "/api/admin/dd-rules", {"sources": catalog["dd_data_sources"]}),
                api_operation("POST", "/api/admin/connectors/office365", catalog["office365_connector"]),
                api_operation("POST", "/api/admin/sharepoint-mapping", catalog["sharepoint_mapping"]),
            ]
        )

    return {
        "status": "ready" if is_legal_admin else "view_only",
        "legal_admin_full_access": is_legal_admin,
        "catalog": catalog,
        "operations": operations,
    }
