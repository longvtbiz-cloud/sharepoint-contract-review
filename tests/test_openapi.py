from governance.contracts import all_api_contracts
from governance.openapi import build_openapi_spec


def _count_contract_strings(value: object) -> int:
    if isinstance(value, str):
        return 1
    if isinstance(value, dict):
        return sum(_count_contract_strings(child) for child in value.values())
    return 0


def test_openapi_spec_includes_runtime_endpoints() -> None:
    spec = build_openapi_spec()

    assert spec["openapi"] == "3.1.0"
    assert spec["paths"]["/health"]["get"]["operationId"] == "runtime_health_get"
    assert spec["paths"]["/invocations"]["post"]["operationId"] == "runtime_invocations_post"
    assert "InvocationPayload" in spec["components"]["schemas"]
    assert "GovernanceResponse" in spec["components"]["schemas"]


def test_openapi_spec_covers_registered_contracts() -> None:
    spec = build_openapi_spec()
    expected_contract_count = _count_contract_strings(all_api_contracts())
    domain_operation_count = 0

    for path_item in spec["paths"].values():
        for operation in path_item.values():
            if operation["tags"] != ["runtime"]:
                domain_operation_count += 1

    assert domain_operation_count == expected_contract_count


def test_openapi_spec_includes_key_domain_paths() -> None:
    spec = build_openapi_spec()

    assert "post" in spec["paths"]["/api/contracts/rounds/create"]
    assert "post" in spec["paths"]["/api/sla/review-tasks/escalations"]
    assert "get" in spec["paths"]["/api/office365/users"]
    assert spec["paths"]["/api/sharepoint/files/{file_id}"]["get"]["tags"] == ["sharepoint"]
