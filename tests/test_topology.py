from governance.topology import build_mermaid, build_topology


def test_topology_contains_expected_agents() -> None:
    topology = build_topology()
    node_ids = {node["id"] for node in topology["nodes"]}

    assert "intake_agent" in node_ids
    assert "dd_gate_agent" in node_ids
    assert "sla_agent" in node_ids
    assert "ai_summary_agent" in node_ids
    assert "tools" in node_ids


def test_topology_contains_critical_conditional_edges() -> None:
    topology = build_topology()
    edges = {(edge["source"], edge["target"], edge.get("condition")) for edge in topology["edges"]}

    assert ("rbac_agent", "access_denied_agent", "access denied") in edges
    assert ("policy_agent", "policy_blocked_agent", "policy violation") in edges
    assert ("dd_gate_agent", "contract_review_agent", "DD allows contract review") in edges
    assert ("dd_gate_agent", "sharepoint_agent", "DD blocks contract review") in edges


def test_mermaid_topology_is_renderable_text() -> None:
    mermaid = build_mermaid()

    assert mermaid.startswith("flowchart TD")
    assert 'intake_agent["Intake Agent"]' in mermaid
    assert '-- "DD allows contract review" -->' in mermaid
