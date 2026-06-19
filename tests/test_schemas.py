from governance.scenarios import SCENARIOS, scenario_payload
from governance.schemas import get_schema, list_schemas
from scripts.validate_governance_flow import invoke


def test_schema_registry_exposes_core_contracts() -> None:
    schemas = list_schemas()

    assert set(schemas) == {
        "agent_catalog",
        "invocation_payload",
        "governance_response",
        "scenario_catalog",
        "topology",
    }
    assert schemas["invocation_payload"]["$schema"] == "https://json-schema.org/draft/2020-12/schema"


def test_scenario_payloads_match_invocation_schema_enums() -> None:
    schema = get_schema("invocation_payload")
    required = set(schema["required"])
    action_enum = set(schema["properties"]["action"]["enum"])
    role_enum = set(schema["properties"]["role"]["enum"])

    for scenario_id in SCENARIOS:
        payload = scenario_payload(scenario_id)
        assert required.issubset(payload), scenario_id
        assert payload["action"] in action_enum, scenario_id
        assert payload["role"] in role_enum, scenario_id


def test_governance_response_has_required_schema_fields() -> None:
    schema = get_schema("governance_response")
    response = invoke(scenario_payload("biz_review_ready"))

    assert set(schema["required"]).issubset(response)
    assert response["status"] in schema["properties"]["status"]["enum"]
    assert response["workflow_status"] in schema["properties"]["workflow_status"]["enum"]


def test_get_schema_returns_copy() -> None:
    schema = get_schema("invocation_payload")
    schema["title"] = "Changed"

    assert get_schema("invocation_payload")["title"] == "Governance Invocation Payload"
