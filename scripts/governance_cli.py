import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from governance.openapi import build_openapi_spec
from governance.scenarios import list_scenarios
from governance.schemas import list_schemas


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


def cmd_scenarios(args: argparse.Namespace) -> None:
    _write_json({"scenarios": list_scenarios()}, args.output)


def cmd_schemas(args: argparse.Namespace) -> None:
    _write_json({"schemas": list_schemas()}, args.output)


def cmd_openapi(args: argparse.Namespace) -> None:
    _write_json(build_openapi_spec(), args.output)


def cmd_artifacts(args: argparse.Namespace) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json({"scenarios": list_scenarios()}, args.output_dir / "governance-scenarios.json")
    _write_json({"schemas": list_schemas()}, args.output_dir / "governance-schemas.json")
    _write_json(build_openapi_spec(), args.output_dir / "governance-openapi.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enterprise Partner Governance Platform helper CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Run deterministic governance smoke checks.")
    validate_parser.set_defaults(func=cmd_validate)

    scenarios_parser = subparsers.add_parser("scenarios", help="Print or write reusable scenario payloads.")
    scenarios_parser.add_argument("--output", type=Path)
    scenarios_parser.set_defaults(func=cmd_scenarios)

    schemas_parser = subparsers.add_parser("schemas", help="Print or write integration JSON schemas.")
    schemas_parser.add_argument("--output", type=Path)
    schemas_parser.set_defaults(func=cmd_schemas)

    openapi_parser = subparsers.add_parser("openapi", help="Print or write the OpenAPI integration scaffold.")
    openapi_parser.add_argument("--output", type=Path)
    openapi_parser.set_defaults(func=cmd_openapi)

    artifacts_parser = subparsers.add_parser("artifacts", help="Write scenarios, schemas, and OpenAPI JSON files.")
    artifacts_parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    artifacts_parser.set_defaults(func=cmd_artifacts)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
