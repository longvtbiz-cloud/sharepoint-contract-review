from copy import deepcopy
from typing import Any

from governance.contracts import all_api_contracts
from governance.schemas import GOVERNANCE_RESPONSE_SCHEMA, INVOCATION_PAYLOAD_SCHEMA


def _operation_id(tag: str, name: str, method: str) -> str:
    parts = [tag, name, method.lower()]
    return "_".join(part.replace("-", "_") for part in parts)


def _parse_contract(contract: str) -> tuple[str, str]:
    method, path = contract.split(" ", 1)
    return method.lower(), path


def _iter_contracts(contracts: dict[str, Any], prefix: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str]]:
    flattened = []
    for key, value in contracts.items():
        current = (*prefix, key)
        if isinstance(value, str):
            flattened.append((current, value))
        elif isinstance(value, dict):
            flattened.extend(_iter_contracts(value, current))
    return flattened


def build_openapi_spec() -> dict[str, Any]:
    paths: dict[str, Any] = {
        "/health": {
            "get": {
                "tags": ["runtime"],
                "operationId": "runtime_health_get",
                "summary": "Check agent health",
                "responses": {
                    "200": {
                        "description": "Agent runtime is healthy.",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        },
        "/invocations": {
            "post": {
                "tags": ["runtime"],
                "operationId": "runtime_invocations_post",
                "summary": "Invoke governance orchestrator",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/InvocationPayload"}}},
                },
                "responses": {
                    "200": {
                        "description": "Governance workflow response.",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/GovernanceResponse"}}},
                    }
                },
            }
        },
    }

    for tag, contracts in all_api_contracts().items():
        for name_parts, contract in _iter_contracts(contracts):
            method, path = _parse_contract(contract)
            name = "_".join(name_parts)
            paths.setdefault(path, {})[method] = {
                "tags": [tag],
                "operationId": _operation_id(tag, name, method),
                "summary": f"{tag.replace('_', ' ').title()} {name.replace('_', ' ')}",
                "responses": {
                    "200": {
                        "description": "Planned integration endpoint response.",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
            if method in {"post", "put", "patch"}:
                paths[path][method]["requestBody"] = {
                    "required": False,
                    "content": {"application/json": {"schema": {"type": "object"}}},
                }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Enterprise Partner Governance Platform API",
            "version": "0.1.0",
            "description": "Integration scaffold for the governance orchestrator and planned domain APIs.",
        },
        "servers": [{"url": "http://127.0.0.1:8080"}],
        "paths": dict(sorted(paths.items())),
        "components": {
            "schemas": {
                "InvocationPayload": deepcopy(INVOCATION_PAYLOAD_SCHEMA),
                "GovernanceResponse": deepcopy(GOVERNANCE_RESPONSE_SCHEMA),
            }
        },
    }
