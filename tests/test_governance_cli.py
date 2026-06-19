import json

from scripts.governance_cli import build_parser
from scripts import governance_cli


def test_cli_parser_exposes_expected_commands() -> None:
    parser = build_parser()

    for command in ["validate", "scenarios", "schemas", "agents", "openapi", "config", "topology", "artifacts"]:
        args = parser.parse_args([command])
        assert args.command == command


def test_cli_artifacts_writes_expected_files(tmp_path) -> None:
    args = build_parser().parse_args(["artifacts", "--output-dir", str(tmp_path)])

    args.func(args)

    agents = json.loads((tmp_path / "governance-agents.json").read_text(encoding="utf-8"))
    config = json.loads((tmp_path / "governance-config.json").read_text(encoding="utf-8"))
    topology = json.loads((tmp_path / "governance-topology.json").read_text(encoding="utf-8"))
    topology_mermaid = (tmp_path / "governance-topology.mmd").read_text(encoding="utf-8")
    scenarios = json.loads((tmp_path / "governance-scenarios.json").read_text(encoding="utf-8"))
    schemas = json.loads((tmp_path / "governance-schemas.json").read_text(encoding="utf-8"))
    openapi = json.loads((tmp_path / "governance-openapi.json").read_text(encoding="utf-8"))
    assert len(agents["agents"]) == 18
    assert len(config["config"]) == 8
    assert len(topology["topology"]["nodes"]) >= 18
    assert topology_mermaid.startswith("flowchart TD")
    assert len(scenarios["scenarios"]) == 12
    assert set(schemas["schemas"]) == {
        "agent_catalog",
        "invocation_payload",
        "governance_response",
        "scenario_catalog",
    }
    assert openapi["openapi"] == "3.1.0"


def test_cli_openapi_writes_output_file(tmp_path) -> None:
    output = tmp_path / "openapi.json"
    args = build_parser().parse_args(["openapi", "--output", str(output)])

    governance_cli.cmd_openapi(args)

    assert json.loads(output.read_text(encoding="utf-8"))["info"]["title"] == (
        "Enterprise Partner Governance Platform API"
    )


def test_cli_agents_writes_output_file(tmp_path) -> None:
    output = tmp_path / "agents.json"
    args = build_parser().parse_args(["agents", "--output", str(output)])

    args.func(args)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["agents"][0]["id"] == "intake_agent"
    assert payload["agents"][-1]["id"] == "tools"


def test_cli_config_writes_validation_result(tmp_path) -> None:
    output = tmp_path / "config.json"
    args = build_parser().parse_args(["config", "--check-mode", "runtime", "--output", str(output)])

    args.func(args)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert len(payload["config"]) == 8
    assert payload["validation"]["status"] == "missing_required_values"


def test_cli_topology_writes_mermaid_file(tmp_path) -> None:
    output = tmp_path / "topology.mmd"
    args = build_parser().parse_args(["topology", "--format", "mermaid", "--output", str(output)])

    args.func(args)

    assert output.read_text(encoding="utf-8").startswith("flowchart TD")
