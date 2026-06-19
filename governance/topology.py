from copy import deepcopy
from typing import Any


NODES: list[dict[str, Any]] = [
    {"id": "START", "label": "Start", "kind": "runtime"},
    {"id": "intake_agent", "label": "Intake Agent", "kind": "deterministic_agent"},
    {"id": "rbac_agent", "label": "RBAC Agent", "kind": "deterministic_agent"},
    {"id": "admin_governance_agent", "label": "Admin Governance Agent", "kind": "deterministic_agent"},
    {"id": "policy_agent", "label": "Critical Policy Agent", "kind": "deterministic_agent"},
    {"id": "dd_gate_agent", "label": "DD Gate Agent", "kind": "deterministic_agent"},
    {"id": "contract_review_agent", "label": "Contract Review Agent", "kind": "deterministic_agent"},
    {"id": "sharepoint_agent", "label": "SharePoint Agent", "kind": "deterministic_agent"},
    {"id": "lifecycle_agent", "label": "Lifecycle Agent", "kind": "deterministic_agent"},
    {"id": "ai_planning_agent", "label": "AI Planning Agent", "kind": "deterministic_agent"},
    {"id": "office365_agent", "label": "Office365 Agent", "kind": "deterministic_agent"},
    {"id": "sla_agent", "label": "SLA Agent", "kind": "deterministic_agent"},
    {"id": "execution_agent", "label": "Execution Planner", "kind": "deterministic_agent"},
    {"id": "audit_persistence_agent", "label": "Audit Persistence Agent", "kind": "deterministic_agent"},
    {"id": "dashboard_agent", "label": "Dashboard Agent", "kind": "deterministic_agent"},
    {"id": "access_denied_agent", "label": "Access Denied Agent", "kind": "terminal_block_agent"},
    {"id": "policy_blocked_agent", "label": "Policy Blocked Agent", "kind": "terminal_block_agent"},
    {"id": "ai_summary_agent", "label": "AI Summary Agent", "kind": "llm_optional_agent"},
    {"id": "tools", "label": "Memory Tools", "kind": "tool_node"},
    {"id": "END", "label": "End", "kind": "runtime"},
]


EDGES: list[dict[str, Any]] = [
    {"source": "START", "target": "intake_agent"},
    {"source": "intake_agent", "target": "rbac_agent"},
    {"source": "rbac_agent", "target": "admin_governance_agent", "condition": "access allowed"},
    {"source": "rbac_agent", "target": "access_denied_agent", "condition": "access denied"},
    {"source": "admin_governance_agent", "target": "policy_agent"},
    {"source": "policy_agent", "target": "dd_gate_agent", "condition": "policy allowed"},
    {"source": "policy_agent", "target": "policy_blocked_agent", "condition": "policy violation"},
    {"source": "access_denied_agent", "target": "ai_summary_agent"},
    {"source": "policy_blocked_agent", "target": "ai_summary_agent"},
    {"source": "dd_gate_agent", "target": "contract_review_agent", "condition": "DD allows contract review"},
    {"source": "dd_gate_agent", "target": "sharepoint_agent", "condition": "DD blocks contract review"},
    {"source": "contract_review_agent", "target": "sharepoint_agent"},
    {"source": "sharepoint_agent", "target": "lifecycle_agent"},
    {"source": "lifecycle_agent", "target": "ai_planning_agent"},
    {"source": "ai_planning_agent", "target": "office365_agent"},
    {"source": "office365_agent", "target": "sla_agent"},
    {"source": "sla_agent", "target": "execution_agent"},
    {"source": "execution_agent", "target": "audit_persistence_agent"},
    {"source": "audit_persistence_agent", "target": "dashboard_agent"},
    {"source": "dashboard_agent", "target": "ai_summary_agent"},
    {"source": "ai_summary_agent", "target": "tools", "condition": "LLM requested tool call"},
    {"source": "tools", "target": "ai_summary_agent"},
    {"source": "ai_summary_agent", "target": "END", "condition": "no tool call"},
]


def build_topology() -> dict[str, Any]:
    return {"nodes": deepcopy(NODES), "edges": deepcopy(EDGES)}


def build_mermaid() -> str:
    labels = {node["id"]: node["label"] for node in NODES}
    lines = ["flowchart TD"]
    for edge in EDGES:
        source = edge["source"]
        target = edge["target"]
        source_label = labels[source]
        target_label = labels[target]
        source_node = f'{source}["{source_label}"]'
        target_node = f'{target}["{target_label}"]'
        condition = edge.get("condition")
        if condition:
            lines.append(f'  {source_node} -- "{condition}" --> {target_node}')
        else:
            lines.append(f"  {source_node} --> {target_node}")
    return "\n".join(lines) + "\n"
