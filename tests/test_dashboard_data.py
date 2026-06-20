from governance.dashboard_data import build_dashboard_data


def test_dashboard_data_exposes_operational_summary() -> None:
    data = build_dashboard_data()

    assert data["summary"]["scenario_count"] == 12
    assert data["summary"]["agent_count"] == 18
    assert data["summary"]["api_contract_count"] > 30
    assert data["summary"]["workflow_counts"]["ready_for_review"] >= 1
    assert data["openapi"]["metadata_paths"] == ["/metadata/agents", "/metadata/topology"]


def test_dashboard_data_scenarios_include_trace_and_visibility() -> None:
    data = build_dashboard_data()
    by_id = {scenario["scenario_id"]: scenario for scenario in data["scenarios"]}

    assert by_id["biz_review_ready"]["decision_trace"][0]["gate"] == "rbac"
    assert by_id["external_partner_limited"]["visibility"] == "external_limited"
    assert by_id["external_partner_limited"]["decision_trace"] == []
