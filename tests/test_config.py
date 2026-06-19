from pathlib import Path

from governance.config import list_config_variables, validate_environment


ROOT = Path(__file__).resolve().parents[1]


def test_env_example_contains_all_catalog_variables() -> None:
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    declared = {line.split("=", 1)[0] for line in env_example.splitlines() if line and not line.startswith("#")}

    assert {variable["name"] for variable in list_config_variables()}.issubset(declared)


def test_validate_environment_reports_missing_runtime_values() -> None:
    result = validate_environment("runtime", environ={})

    assert result["status"] == "missing_required_values"
    assert result["missing"] == ["GREENNODE_CLIENT_ID", "GREENNODE_CLIENT_SECRET"]


def test_validate_environment_accepts_required_runtime_values() -> None:
    result = validate_environment(
        "runtime",
        environ={
            "GREENNODE_CLIENT_ID": "client",
            "GREENNODE_CLIENT_SECRET": "secret",
        },
    )

    assert result == {"mode": "runtime", "status": "ready", "missing": []}
