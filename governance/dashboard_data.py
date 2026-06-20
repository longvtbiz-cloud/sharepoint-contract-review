from copy import deepcopy
from typing import Any, Callable

from governance.agent_catalog import list_agents
from governance.config import list_config_variables, validate_environment
from governance.contracts import all_api_contracts
from governance.openapi import build_openapi_spec
from governance.scenarios import list_scenarios
from governance.schemas import list_schemas
from governance.topology import build_topology


def _count_contracts(value: Any) -> int:
    if isinstance(value, str):
        return 1
    if isinstance(value, dict):
        return sum(_count_contracts(child) for child in value.values())
    return 0


def _workflow_counts(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for scenario in scenarios:
        status = scenario["actual_workflow_status"]
        counts[status] = counts.get(status, 0) + 1
    return counts


def _risk_counts(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for scenario in scenarios:
        risk = scenario.get("risk_level") or "Hidden"
        counts[risk] = counts.get(risk, 0) + 1
    return counts


def build_dashboard_data(invoker: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    if invoker is None:
        from scripts.validate_governance_flow import invoke

        invoker = invoke

    scenario_rows = []
    for scenario in list_scenarios():
        response = invoker(scenario["payload"])
        dashboard_snapshot = response.get("dashboard_snapshot") or {}
        dd_result = response.get("dd_result") or {}
        scenario_rows.append(
            {
                "scenario_id": scenario["scenario_id"],
                "title": scenario["title"],
                "partner_name": scenario["payload"].get("partner_name"),
                "action": scenario["payload"].get("action"),
                "role": scenario["payload"].get("role"),
                "expected_workflow_status": scenario["expected_workflow_status"],
                "actual_workflow_status": response.get("workflow_status"),
                "risk_level": dd_result.get("risk_level"),
                "audit_event_count": len(response.get("audit_events", [])),
                "execution_steps": (response.get("execution_plan") or {}).get("total_steps", 0),
                "decision_trace": response.get("decision_trace", []),
                "dashboard_snapshot": dashboard_snapshot,
                "visibility": response.get("visibility", "internal"),
            }
        )

    topology = build_topology()
    openapi = build_openapi_spec()
    contracts = all_api_contracts()
    schemas = list_schemas()
    agents = list_agents()
    config = list_config_variables()

    return {
        "summary": {
            "scenario_count": len(scenario_rows),
            "agent_count": len(agents),
            "topology_node_count": len(topology["nodes"]),
            "topology_edge_count": len(topology["edges"]),
            "api_contract_count": _count_contracts(contracts),
            "openapi_path_count": len(openapi["paths"]),
            "schema_count": len(schemas),
            "workflow_counts": _workflow_counts(scenario_rows),
            "risk_counts": _risk_counts(scenario_rows),
        },
        "scenarios": scenario_rows,
        "agents": agents,
        "topology": topology,
        "contracts": deepcopy(contracts),
        "schemas": sorted(schemas),
        "config": {
            "variables": config,
            "validation": {
                "runtime": validate_environment("runtime"),
                "deploy": validate_environment("deploy"),
                "ai_summary": validate_environment("ai_summary"),
                "agentbase_memory": validate_environment("agentbase_memory"),
            },
        },
        "openapi": {
            "version": openapi["openapi"],
            "title": openapi["info"]["title"],
            "path_count": len(openapi["paths"]),
            "metadata_paths": sorted(path for path in openapi["paths"] if path.startswith("/metadata/")),
        },
    }
