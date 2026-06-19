from governance.agent_catalog import get_agent, list_agents
from governance.topology import build_topology


def test_agent_catalog_covers_executable_topology_nodes() -> None:
    agents = {agent["id"]: agent for agent in list_agents()}
    topology_nodes = {
        node["id"]
        for node in build_topology()["nodes"]
        if node["kind"] not in {"runtime"}
    }

    assert set(agents) == topology_nodes


def test_agent_catalog_handoffs_are_topology_edges() -> None:
    topology_edges = {
        (edge["source"], edge["target"])
        for edge in build_topology()["edges"]
        if edge["target"] != "END"
    }

    for agent in list_agents():
        for handoff in agent["handoffs"]:
            if handoff == "END":
                continue
            assert (agent["id"], handoff) in topology_edges


def test_get_agent_returns_copy() -> None:
    agent = get_agent("dd_gate_agent")
    agent["label"] = "Changed"

    assert get_agent("dd_gate_agent")["label"] == "DD Gate Agent"
