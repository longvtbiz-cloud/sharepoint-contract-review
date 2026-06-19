from scripts import validate_governance_flow as flow


def test_biz_ticket_can_reach_review() -> None:
    flow.assert_biz_ticket_can_reach_review()


def test_dd_blocks_contract_review() -> None:
    flow.assert_dd_blocks_contract_review()


def test_dd_rulebook_rejects_critical_findings() -> None:
    flow.assert_dd_rulebook_rejects_critical_findings()


def test_missing_mandatory_department_blocks_round_readiness() -> None:
    flow.assert_missing_mandatory_department_blocks_round_readiness()


def test_external_partner_visibility_is_limited() -> None:
    flow.assert_external_partner_visibility_is_limited()


def test_partner_request_uses_biz_gate_and_limited_visibility() -> None:
    flow.assert_partner_request_uses_biz_gate_and_limited_visibility()


def test_termination_workflow_is_planned() -> None:
    flow.assert_termination_workflow_is_planned()


def test_legal_admin_gets_full_governance_plan() -> None:
    flow.assert_legal_admin_gets_full_governance_plan()


def test_counterparty_send_requires_completed_internal_review() -> None:
    flow.assert_counterparty_send_requires_completed_internal_review()


def test_signing_requires_final_approval() -> None:
    flow.assert_signing_requires_final_approval()


def test_override_requires_reason_and_risk_acceptance() -> None:
    flow.assert_override_requires_reason_and_risk_acceptance()


def test_high_priority_review_uses_short_sla() -> None:
    flow.assert_high_priority_review_uses_short_sla()


def test_metadata_agents_action_returns_catalog() -> None:
    result = flow.invoke({"action": "metadata.agents"})

    assert result["metadata_kind"] == "agents"
    assert result["agents"][0]["id"] == "intake_agent"


def test_metadata_topology_action_can_return_mermaid() -> None:
    result = flow.invoke({"action": "metadata.topology", "format": "mermaid"})

    assert result["metadata_kind"] == "topology"
    assert result["topology"]["nodes"][0]["id"] == "START"
    assert result["mermaid"].startswith("flowchart TD")


def test_metadata_openapi_action_returns_spec() -> None:
    result = flow.invoke({"action": "metadata.openapi"})

    assert result["metadata_kind"] == "openapi"
    assert result["openapi"]["openapi"] == "3.1.0"
