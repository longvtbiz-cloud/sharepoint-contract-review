import json

from scripts.governance_cli import build_parser
from scripts import governance_cli


def test_cli_parser_exposes_expected_commands() -> None:
    parser = build_parser()

    for command in ["validate", "scenarios", "schemas", "openapi", "artifacts"]:
        args = parser.parse_args([command])
        assert args.command == command


def test_cli_artifacts_writes_expected_files(tmp_path) -> None:
    args = build_parser().parse_args(["artifacts", "--output-dir", str(tmp_path)])

    args.func(args)

    scenarios = json.loads((tmp_path / "governance-scenarios.json").read_text(encoding="utf-8"))
    schemas = json.loads((tmp_path / "governance-schemas.json").read_text(encoding="utf-8"))
    openapi = json.loads((tmp_path / "governance-openapi.json").read_text(encoding="utf-8"))
    assert len(scenarios["scenarios"]) == 12
    assert set(schemas["schemas"]) == {"invocation_payload", "governance_response", "scenario_catalog"}
    assert openapi["openapi"] == "3.1.0"


def test_cli_openapi_writes_output_file(tmp_path) -> None:
    output = tmp_path / "openapi.json"
    args = build_parser().parse_args(["openapi", "--output", str(output)])

    governance_cli.cmd_openapi(args)

    assert json.loads(output.read_text(encoding="utf-8"))["info"]["title"] == (
        "Enterprise Partner Governance Platform API"
    )
