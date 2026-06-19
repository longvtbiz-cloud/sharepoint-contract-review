import pytest

from governance.scenarios import SCENARIOS, list_scenarios, scenario_payload
from scripts.validate_governance_flow import invoke


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_scenario_expected_workflow_status(scenario_id: str) -> None:
    result = invoke(scenario_payload(scenario_id))
    assert result["workflow_status"] == SCENARIOS[scenario_id]["expected_workflow_status"]


def test_scenario_payload_returns_copy() -> None:
    payload = scenario_payload("biz_review_ready")
    payload["partner_name"] = "Changed Partner"

    assert scenario_payload("biz_review_ready")["partner_name"] == "Haidilao"


def test_list_scenarios_exposes_catalog_metadata() -> None:
    scenarios = list_scenarios()

    assert len(scenarios) == 12
    assert {scenario["scenario_id"] for scenario in scenarios} == set(SCENARIOS)
    assert all("payload" in scenario for scenario in scenarios)
