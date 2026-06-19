from governance.trace import build_decision_trace
from governance.scenarios import scenario_payload
from scripts.validate_governance_flow import invoke


def test_decision_trace_records_happy_path_gates() -> None:
    result = invoke(scenario_payload("biz_review_ready"))

    gates = [step["gate"] for step in result["decision_trace"]]
    assert gates == [
        "rbac",
        "critical_policy",
        "dd_gate",
        "review_matrix",
        "sla",
        "execution",
        "audit_persistence",
    ]
    assert result["decision_trace"][0]["decision"] == "allow"
    assert result["decision_trace"][-1]["reasons"] == ["Audit events: 10"]


def test_decision_trace_stops_at_blocking_policy() -> None:
    result = invoke(scenario_payload("counterparty_send_policy_block"))

    assert [step["gate"] for step in result["decision_trace"]] == ["rbac", "critical_policy"]
    assert result["decision_trace"][-1]["status"] == "blocked"


def test_decision_trace_returns_copy() -> None:
    result = {"access_result": {"allowed": True}, "policy_result": {"allowed": True}}
    trace = build_decision_trace(result)
    trace[0]["gate"] = "changed"

    assert build_decision_trace(result)[0]["gate"] == "rbac"
