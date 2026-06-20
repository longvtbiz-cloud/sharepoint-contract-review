import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from governance.agent_catalog import list_agents
from governance.config import list_config_variables, validate_environment
from governance.dashboard_data import build_dashboard_data
from governance.openapi import build_openapi_spec
from governance.scenarios import list_scenarios
from governance.schemas import list_schemas
from governance.schema_validation import validate_against_schema
from governance.topology import build_mermaid, build_topology


def _write_json(payload: dict, output: Path | None) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def cmd_validate(_args: argparse.Namespace) -> None:
    from scripts import validate_governance_flow

    validate_governance_flow.run_all_checks()


def cmd_contract_check(args: argparse.Namespace) -> None:
    from scripts.validate_governance_flow import invoke

    schemas = list_schemas()
    checks = []

    for scenario in list_scenarios():
        scenario_id = scenario["scenario_id"]
        payload_issues = validate_against_schema(scenario["payload"], schemas["invocation_payload"])
        response = invoke(scenario["payload"])
        response_issues = validate_against_schema(response, schemas["governance_response"])
        checks.append(
            {
                "target": f"scenario:{scenario_id}",
                "status": "pass" if not payload_issues and not response_issues else "fail",
                "issues": [*payload_issues, *response_issues],
            }
        )

    metadata_targets = {
        "agent_catalog": ({"agents": list_agents()}, schemas["agent_catalog"]),
        "topology": (build_topology(), schemas["topology"]),
    }
    for target, (payload, schema) in metadata_targets.items():
        issues = validate_against_schema(payload, schema)
        checks.append({"target": target, "status": "pass" if not issues else "fail", "issues": issues})

    failed = [check for check in checks if check["status"] != "pass"]
    payload = {
        "status": "pass" if not failed else "fail",
        "checks": len(checks),
        "failed": len(failed),
        "results": checks if args.verbose or failed else [],
    }
    _write_json(payload, args.output)
    if failed:
        raise SystemExit(1)


def cmd_scenarios(args: argparse.Namespace) -> None:
    _write_json({"scenarios": list_scenarios()}, args.output)


def cmd_schemas(args: argparse.Namespace) -> None:
    _write_json({"schemas": list_schemas()}, args.output)


def cmd_agents(args: argparse.Namespace) -> None:
    _write_json({"agents": list_agents()}, args.output)


def cmd_openapi(args: argparse.Namespace) -> None:
    _write_json(build_openapi_spec(), args.output)


def cmd_artifacts(args: argparse.Namespace) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json({"agents": list_agents()}, args.output_dir / "governance-agents.json")
    _write_json({"config": list_config_variables()}, args.output_dir / "governance-config.json")
    _write_json({"topology": build_topology()}, args.output_dir / "governance-topology.json")
    (args.output_dir / "governance-topology.mmd").write_text(build_mermaid(), encoding="utf-8")
    _write_json({"scenarios": list_scenarios()}, args.output_dir / "governance-scenarios.json")
    _write_json({"schemas": list_schemas()}, args.output_dir / "governance-schemas.json")
    _write_json(build_openapi_spec(), args.output_dir / "governance-openapi.json")


def cmd_dashboard(args: argparse.Namespace) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(build_dashboard_data(), args.output_dir / "data.json")


def cmd_config(args: argparse.Namespace) -> None:
    payload = {"config": list_config_variables()}
    if args.check_mode:
        payload["validation"] = validate_environment(args.check_mode)
    _write_json(payload, args.output)


def cmd_topology(args: argparse.Namespace) -> None:
    if args.format == "mermaid":
        text = build_mermaid()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        return
    _write_json({"topology": build_topology()}, args.output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enterprise Partner Governance Platform helper CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Run deterministic governance smoke checks.")
    validate_parser.set_defaults(func=cmd_validate)

    contract_parser = subparsers.add_parser("contract-check", help="Validate scenarios and metadata against schemas.")
    contract_parser.add_argument("--output", type=Path)
    contract_parser.add_argument("--verbose", action="store_true")
    contract_parser.set_defaults(func=cmd_contract_check)

    scenarios_parser = subparsers.add_parser("scenarios", help="Print or write reusable scenario payloads.")
    scenarios_parser.add_argument("--output", type=Path)
    scenarios_parser.set_defaults(func=cmd_scenarios)

    schemas_parser = subparsers.add_parser("schemas", help="Print or write integration JSON schemas.")
    schemas_parser.add_argument("--output", type=Path)
    schemas_parser.set_defaults(func=cmd_schemas)

    agents_parser = subparsers.add_parser("agents", help="Print or write multi-agent responsibility metadata.")
    agents_parser.add_argument("--output", type=Path)
    agents_parser.set_defaults(func=cmd_agents)

    openapi_parser = subparsers.add_parser("openapi", help="Print or write the OpenAPI integration scaffold.")
    openapi_parser.add_argument("--output", type=Path)
    openapi_parser.set_defaults(func=cmd_openapi)

    config_parser = subparsers.add_parser("config", help="Print or write runtime configuration metadata.")
    config_parser.add_argument("--output", type=Path)
    config_parser.add_argument("--check-mode", choices=["deploy", "runtime", "ai_summary", "agentbase_memory"])
    config_parser.set_defaults(func=cmd_config)

    topology_parser = subparsers.add_parser("topology", help="Print or write LangGraph topology metadata.")
    topology_parser.add_argument("--format", choices=["json", "mermaid"], default="json")
    topology_parser.add_argument("--output", type=Path)
    topology_parser.set_defaults(func=cmd_topology)

    artifacts_parser = subparsers.add_parser("artifacts", help="Write scenarios, schemas, and OpenAPI JSON files.")
    artifacts_parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    artifacts_parser.set_defaults(func=cmd_artifacts)

    dashboard_parser = subparsers.add_parser("dashboard", help="Refresh local dashboard data.")
    dashboard_parser.add_argument("--output-dir", type=Path, default=Path("dashboard"))
    dashboard_parser.set_defaults(func=cmd_dashboard)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
