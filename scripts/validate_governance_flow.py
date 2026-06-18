import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


def invoke(payload: dict) -> dict:
    context = SimpleNamespace(session_id="validation-session", user_id="validation-user", request_headers={})
    return main.handler(payload, context)


def assert_biz_ticket_can_reach_review() -> None:
    result = invoke(
        {
            "action": "ticket.create",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000001",
            "partner_name": "Haidilao",
            "tax_code": "123456789",
            "project_case": "DieuChinhPhi",
            "created_by": "biz.user",
            "dd_status": "Pass",
            "selected_departments": ["Legal", "FA"],
            "contract_signals": ["contains_payment_terms"],
        }
    )
    assert result["workflow_status"] == "ready_for_review", result
    assert result["dd_result"]["contract_review_allowed"] is True, result
    assert result["dd_result"]["risk_level"] == "Unknown", result
    assert result["review_plan"]["status"] == "Ready", result
    assert len(result["audit_events"]) == 5, result
    assert result["sharepoint_plan"]["operations"][0]["path"] == "/api/sharepoint/folders/create", result
    assert result["api_contracts"]["sharepoint"]["create_folder"] == "POST /api/sharepoint/folders/create", result


def assert_dd_blocks_contract_review() -> None:
    result = invoke(
        {
            "action": "ticket.create",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000003",
            "partner_name": "Blocked Partner",
            "project_case": "NewCooperation",
            "created_by": "biz.user",
            "dd_status": "Pending",
            "selected_departments": ["Legal"],
        }
    )
    assert result["workflow_status"] == "blocked", result
    assert result["dd_result"]["contract_review_allowed"] is False, result
    assert result.get("review_plan") is None, result


def assert_dd_rulebook_rejects_critical_findings() -> None:
    result = invoke(
        {
            "action": "ticket.create",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000004",
            "partner_name": "Critical Partner",
            "project_case": "NewCooperation",
            "created_by": "biz.user",
            "dd_findings": ["sanctions_match"],
            "selected_departments": ["Legal"],
        }
    )
    assert result["workflow_status"] == "blocked", result
    assert result["dd_result"]["dd_status"] == "Reject", result
    assert result["dd_result"]["risk_level"] == "Critical", result
    assert result["dd_result"]["data_source_plan"]["operations"][0]["path"] == "/api/data-sources/{source_id}/sync", result


def assert_external_partner_visibility_is_limited() -> None:
    result = invoke(
        {
            "action": "ticket.create",
            "role": "EXTERNAL_PARTNER",
            "ticket_id": "TCK-000002",
            "partner_name": "External Co",
            "project_case": "PartnerRequest",
            "created_by": "partner.user",
            "dd_status": "Pending",
        }
    )
    assert result["workflow_status"] == "blocked", result
    assert result["visibility"] == "external_limited", result
    assert "dd_result" not in result, result
    assert "audit_events" not in result, result
    assert "api_contracts" not in result, result
    assert result["access_result"]["allowed"] is False, result


if __name__ == "__main__":
    assert_biz_ticket_can_reach_review()
    assert_dd_blocks_contract_review()
    assert_dd_rulebook_rejects_critical_findings()
    assert_external_partner_visibility_is_limited()
    print(json.dumps({"status": "pass", "checks": 4}, indent=2))
