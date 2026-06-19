from copy import deepcopy
from typing import Any


INVOCATION_PAYLOAD_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://enterprise-partner-governance-platform.local/schemas/invocation-payload.json",
    "title": "Governance Invocation Payload",
    "type": "object",
    "additionalProperties": True,
    "required": ["action", "role", "ticket_id", "partner_name", "project_case", "created_by"],
    "properties": {
        "action": {
            "type": "string",
            "enum": [
                "admin.configure",
                "contract.review.start",
                "counterparty.receive",
                "counterparty.send",
                "document.upload",
                "partner.request.submit",
                "review.complete",
                "signing.finalize",
                "termination.create",
                "ticket.create",
                "ticket.view",
                "workflow.override",
            ],
        },
        "role": {
            "type": "string",
            "enum": [
                "BIZ_MANAGER",
                "BIZ_OWNER",
                "COMPLIANCE_MANAGER",
                "COMPLIANCE_REVIEWER",
                "DD_MANAGER",
                "DD_REVIEWER",
                "EXTERNAL_PARTNER",
                "FA_MANAGER",
                "FA_REVIEWER",
                "LEGAL_ADMIN",
                "LEGAL_MANAGER",
                "LEGAL_REVIEWER",
                "OPS_MANAGER",
                "OPS_REVIEWER",
                "PDPA_REVIEWER",
                "PRODUCT_REVIEWER",
                "RISK_MANAGER",
                "RISK_REVIEWER",
                "SECURITY_REVIEWER",
                "VIEW_ONLY",
            ],
        },
        "ticket_id": {"type": "string", "minLength": 1},
        "ticket_type": {"type": "string"},
        "partner_name": {"type": "string", "minLength": 1},
        "tax_code": {"type": "string"},
        "project_case": {"type": "string", "minLength": 1},
        "created_by": {"type": "string", "minLength": 1},
        "actor": {"type": "string"},
        "source": {"type": "string"},
        "priority": {"type": "string", "enum": ["Low", "Normal", "High", "Urgent"]},
        "status": {"type": "string"},
        "contract_type": {"type": "string"},
        "contract_signals": {"type": "array", "items": {"type": "string"}},
        "selected_departments": {"type": "array", "items": {"type": "string"}},
        "dd_status": {
            "type": "string",
            "enum": ["Pending", "In Review", "Need More Info", "Pass", "Conditional Pass", "Reject"],
        },
        "dd_findings": {"type": "array", "items": {"type": "string"}},
        "internal_review_status": {"type": "string"},
        "final_approval_status": {"type": "string"},
        "override_reason": {"type": "string"},
        "risk_acceptance": {"type": "string"},
        "due_date": {"type": "string"},
    },
}


GOVERNANCE_RESPONSE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://enterprise-partner-governance-platform.local/schemas/governance-response.json",
    "title": "Governance Orchestrator Response",
    "type": "object",
    "additionalProperties": True,
    "required": ["status", "ticket", "access_result", "workflow_status", "ai_summary", "timestamp"],
    "properties": {
        "status": {"type": "string", "enum": ["success", "error"]},
        "ticket": {"type": ["object", "null"]},
        "access_result": {"type": ["object", "null"]},
        "admin_plan": {"type": ["object", "null"]},
        "policy_result": {"type": ["object", "null"]},
        "dd_result": {"type": ["object", "null"]},
        "review_plan": {"type": ["object", "null"]},
        "sharepoint_plan": {"type": ["object", "null"]},
        "negotiation_plan": {"type": ["object", "null"]},
        "partner_portal_plan": {"type": ["object", "null"]},
        "termination_plan": {"type": ["object", "null"]},
        "ai_plan": {"type": ["object", "null"]},
        "office365_plan": {"type": ["object", "null"]},
        "sla_plan": {"type": ["object", "null"]},
        "execution_plan": {"type": ["object", "null"]},
        "audit_plan": {"type": ["object", "null"]},
        "dashboard_snapshot": {"type": ["object", "null"]},
        "audit_events": {"type": "array", "items": {"type": "object"}},
        "api_contracts": {"type": "object"},
        "workflow_status": {
            "type": ["string", "null"],
            "enum": ["draft", "blocked", "ready_for_review", "reviewer_selection_incomplete", None],
        },
        "ai_summary": {"type": ["string", "null"]},
        "timestamp": {"type": "string"},
        "visibility": {"type": "string", "enum": ["external_limited"]},
    },
}


SCENARIO_CATALOG_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://enterprise-partner-governance-platform.local/schemas/scenario-catalog.json",
    "title": "Governance Scenario Catalog",
    "type": "object",
    "required": ["scenarios"],
    "properties": {
        "scenarios": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["scenario_id", "title", "expected_workflow_status", "payload"],
                "properties": {
                    "scenario_id": {"type": "string"},
                    "title": {"type": "string"},
                    "expected_workflow_status": {
                        "type": "string",
                        "enum": ["blocked", "ready_for_review", "reviewer_selection_incomplete"],
                    },
                    "payload": INVOCATION_PAYLOAD_SCHEMA,
                },
            },
        }
    },
}


AGENT_CATALOG_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://enterprise-partner-governance-platform.local/schemas/agent-catalog.json",
    "title": "Governance Agent Catalog",
    "type": "object",
    "required": ["agents"],
    "properties": {
        "agents": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "label", "purpose", "owns", "reads", "writes", "handoffs", "guardrails"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "purpose": {"type": "string"},
                    "owns": {"type": "array", "items": {"type": "string"}},
                    "reads": {"type": "array", "items": {"type": "string"}},
                    "writes": {"type": "array", "items": {"type": "string"}},
                    "handoffs": {"type": "array", "items": {"type": "string"}},
                    "guardrails": {"type": "array", "items": {"type": "string"}},
                },
            },
        }
    },
}


SCHEMAS: dict[str, dict[str, Any]] = {
    "agent_catalog": AGENT_CATALOG_SCHEMA,
    "invocation_payload": INVOCATION_PAYLOAD_SCHEMA,
    "governance_response": GOVERNANCE_RESPONSE_SCHEMA,
    "scenario_catalog": SCENARIO_CATALOG_SCHEMA,
}


def list_schemas() -> dict[str, dict[str, Any]]:
    return deepcopy(SCHEMAS)


def get_schema(schema_id: str) -> dict[str, Any]:
    if schema_id not in SCHEMAS:
        raise KeyError(f"Unknown schema: {schema_id}")
    return deepcopy(SCHEMAS[schema_id])
