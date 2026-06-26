import json

from scripts.serve_dashboard import build_parser, refresh_dashboard_data


def test_serve_dashboard_parser_supports_once_mode() -> None:
    args = build_parser().parse_args(["--port", "8099", "--once"])

    assert args.port == 8099
    assert args.once is True


def test_refresh_dashboard_data_writes_data_json(tmp_path) -> None:
    output = refresh_dashboard_data(tmp_path)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert output.name == "data.json"
    assert payload["summary"]["scenario_count"] == 12
    assert payload["summary"]["agent_count"] == 18
