import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main
from governance.scenarios import scenario_payload


def invoke(payload: dict) -> dict:
    context = SimpleNamespace(session_id="validation-session", user_id="validation-user", request_headers={})
    return main.handler(payload, context)


def assert_biz_ticket_can_reach_review() -> None:
    result = invoke(scenario_payload("biz_review_ready"))
    assert result["workflow_status"] == "ready_for_review", result
    assert result["dd_result"]["contract_review_allowed"] is True, result
    assert result["dd_result"]["risk_level"] == "Unknown", result
    assert result["review_plan"]["status"] == "Ready", result
    assert result["review_plan"]["operations"][0]["path"] == "/api/contracts/rounds/create", result
    assert len(result["review_plan"]["reviewer_tasks"]) == 2, result
    assert len(result["audit_events"]) == 10, result
    assert result["sharepoint_plan"]["operations"][0]["path"] == "/api/sharepoint/folders/create", result
    assert result["api_contracts"]["sharepoint"]["create_folder"] == "POST /api/sharepoint/folders/create", result
    assert result["office365_plan"]["status"] == "inactive_until_configured", result
    assert "Mail.Send" in result["office365_plan"]["scopes"], result
    assert result["api_contracts"]["office365"]["send_mail"] == "POST /api/office365/mail/send", result
    assert result["sla_plan"]["status"] == "planned", result
    assert result["sla_plan"]["operations"][0]["path"] == "/api/sla/review-tasks/schedule-reminders", result
    assert result["api_contracts"]["sla"]["overdue_scan"] == "POST /api/sla/review-tasks/overdue-scan", result
    assert result["admin_plan"]["catalog"]["override_policy"]["requires_reason"] is True, result
    assert result["policy_result"]["allowed"] is True, result
    assert result["ai_plan"]["operations"][0]["path"] == "/api/ai/dd/analyze", result
    assert result["dashboard_snapshot"]["counters"]["contracts_in_review"] == 1, result
    assert result["dashboard_snapshot"]["reviews_by_department"]["Legal"] == 1, result
    assert result["execution_plan"]["status"] == "planned", result
    assert result["execution_plan"]["total_steps"] > 0, result
    assert result["execution_plan"]["steps"][0]["requires_audit_log"] is True, result
    assert result["audit_plan"]["storage_target"] == "99_Audit_Trail", result
    assert result["audit_plan"]["operations"][1]["path"] == "/api/admin/audit-logs", result
    assert result["audit_plan"]["step_audit_links"][0]["requires_audit_log"] is True, result
    assert result["api_contracts"]["ai"]["termination_checklist"] == "POST /api/ai/termination/checklist", result


def assert_dd_blocks_contract_review() -> None:
    result = invoke(scenario_payload("dd_pending_blocks_review"))
    assert result["workflow_status"] == "blocked", result
    assert result["dd_result"]["contract_review_allowed"] is False, result
    assert result.get("review_plan") is None, result


def assert_dd_rulebook_rejects_critical_findings() -> None:
    result = invoke(scenario_payload("dd_critical_findings_reject"))
    assert result["workflow_status"] == "blocked", result
    assert result["dd_result"]["dd_status"] == "Reject", result
    assert result["dd_result"]["risk_level"] == "Critical", result
    assert result["dd_result"]["data_source_plan"]["operations"][0]["path"] == "/api/data-sources/{source_id}/sync", result


def assert_missing_mandatory_department_blocks_round_readiness() -> None:
    result = invoke(scenario_payload("mandatory_department_missing"))
    assert result["workflow_status"] == "reviewer_selection_incomplete", result
    assert result["review_plan"]["status"] == "Reviewer Selection Incomplete", result
    assert result["review_plan"]["missing_mandatory_departments"] == ["PDPA"], result
    assert result["sla_plan"]["status"] == "blocked_until_reviewer_selection_complete", result


def assert_external_partner_visibility_is_limited() -> None:
    result = invoke(scenario_payload("external_partner_limited"))
    assert result["workflow_status"] == "blocked", result
    assert result["visibility"] == "external_limited", result
    assert "dd_result" not in result, result
    assert "audit_events" not in result, result
    assert "api_contracts" not in result, result
    assert "ai_plan" not in result, result
    assert "office365_plan" not in result, result
    assert "sla_plan" not in result, result
    assert "admin_plan" not in result, result
    assert "execution_plan" not in result, result
    assert "audit_plan" not in result, result
    assert "dashboard_snapshot" not in result, result
    assert result["access_result"]["allowed"] is False, result


def assert_partner_request_uses_biz_gate_and_limited_visibility() -> None:
    result = invoke(scenario_payload("partner_request_biz_gate"))
    assert result["workflow_status"] == "blocked", result
    assert result["visibility"] == "external_limited", result
    assert result["partner_portal_plan"]["biz_gate"]["stage"] == "Biz Preliminary Assessment", result
    assert "negotiation_plan" not in result, result


def assert_termination_workflow_is_planned() -> None:
    result = invoke(scenario_payload("termination_planned"))
    assert result["termination_plan"]["operations"][0]["path"] == "/api/termination/workflows/create", result
    assert result["termination_plan"]["stages"][-1] == "Archive", result
    assert result["api_contracts"]["termination"]["archive"] == "POST /api/termination/workflows/{termination_id}/archive", result
    assert result["ai_plan"]["operations"][-1]["path"] == "/api/ai/termination/checklist", result
    assert result["dashboard_snapshot"]["counters"]["termination_pending"] == 1, result


def assert_legal_admin_gets_full_governance_plan() -> None:
    result = invoke(scenario_payload("legal_admin_governance"))
    assert result["admin_plan"]["legal_admin_full_access"] is True, result
    assert result["admin_plan"]["operations"][1]["path"] == "/api/admin/users", result
    assert result["api_contracts"]["admin"]["connectors"]["office365"] == "POST /api/admin/connectors/office365", result


def assert_counterparty_send_requires_completed_internal_review() -> None:
    result = invoke(scenario_payload("counterparty_send_policy_block"))
    assert result["workflow_status"] == "blocked", result
    assert result["policy_result"]["allowed"] is False, result
    assert result["policy_result"]["violations"][0]["code"] == "NO_COUNTERPARTY_SEND_BEFORE_INTERNAL_REVIEW", result
    assert result.get("dd_result") is None, result


def assert_signing_requires_final_approval() -> None:
    result = invoke(scenario_payload("signing_policy_block"))
    assert result["workflow_status"] == "blocked", result
    assert result["policy_result"]["violations"][0]["code"] == "NO_SIGNING_BEFORE_FINAL_APPROVAL", result


def assert_override_requires_reason_and_risk_acceptance() -> None:
    result = invoke(scenario_payload("override_policy_block"))
    violation_codes = {violation["code"] for violation in result["policy_result"]["violations"]}
    assert result["workflow_status"] == "blocked", result
    assert "OVERRIDE_REASON_REQUIRED" in violation_codes, result
    assert "OVERRIDE_RISK_ACCEPTANCE_REQUIRED" in violation_codes, result


def assert_high_priority_review_uses_short_sla() -> None:
    result = invoke(scenario_payload("urgent_review_short_sla"))
    assert result["workflow_status"] == "ready_for_review", result
    assert result["sla_plan"]["sla_hours"] == 24, result
    assert result["sla_plan"]["operations"][1]["path"] == "/api/sla/review-tasks/escalations", result
    assert result["execution_plan"]["steps"][-1]["source_plan"] == "sla_plan", result


def assert_metadata_actions_return_discovery_payloads() -> None:
    agents = invoke({"action": "metadata.agents"})
    topology = invoke({"action": "metadata.topology", "format": "mermaid"})
    openapi = invoke({"action": "metadata.openapi"})

    assert agents["metadata_kind"] == "agents", agents
    assert agents["agents"][0]["id"] == "intake_agent", agents
    assert topology["metadata_kind"] == "topology", topology
    assert topology["topology"]["nodes"][0]["id"] == "START", topology
    assert topology["mermaid"].startswith("flowchart TD"), topology
    assert openapi["metadata_kind"] == "openapi", openapi
    assert openapi["openapi"]["openapi"] == "3.1.0", openapi


def run_all_checks() -> None:
    assert_biz_ticket_can_reach_review()
    assert_dd_blocks_contract_review()
    assert_dd_rulebook_rejects_critical_findings()
    assert_missing_mandatory_department_blocks_round_readiness()
    assert_external_partner_visibility_is_limited()
    assert_partner_request_uses_biz_gate_and_limited_visibility()
    assert_termination_workflow_is_planned()
    assert_legal_admin_gets_full_governance_plan()
    assert_counterparty_send_requires_completed_internal_review()
    assert_signing_requires_final_approval()
    assert_override_requires_reason_and_risk_acceptance()
    assert_high_priority_review_uses_short_sla()
    assert_metadata_actions_return_discovery_payloads()
    print(json.dumps({"status": "pass", "checks": 13}, indent=2))


if __name__ == "__main__":
    run_all_checks()
