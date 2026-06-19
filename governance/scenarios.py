from copy import deepcopy
from typing import Any


SCENARIOS: dict[str, dict[str, Any]] = {
    "biz_review_ready": {
        "title": "Biz ticket can reach contract review",
        "payload": {
            "action": "ticket.create",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000001",
            "partner_name": "Haidilao",
            "tax_code": "123456789",
            "project_case": "DieuChinhPhi",
            "created_by": "biz.user",
            "dd_status": "Pass",
            "selected_departments": ["Legal", "FA"],
            "contract_signals": ["contains_payment_terms"],
        },
        "expected_workflow_status": "ready_for_review",
    },
    "dd_pending_blocks_review": {
        "title": "Pending DD blocks contract review",
        "payload": {
            "action": "ticket.create",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000003",
            "partner_name": "Blocked Partner",
            "project_case": "NewCooperation",
            "created_by": "biz.user",
            "dd_status": "Pending",
            "selected_departments": ["Legal"],
        },
        "expected_workflow_status": "blocked",
    },
    "dd_critical_findings_reject": {
        "title": "Critical DD findings reject the partner",
        "payload": {
            "action": "ticket.create",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000004",
            "partner_name": "Critical Partner",
            "project_case": "NewCooperation",
            "created_by": "biz.user",
            "dd_findings": ["sanctions_match"],
            "selected_departments": ["Legal"],
        },
        "expected_workflow_status": "blocked",
    },
    "mandatory_department_missing": {
        "title": "Missing mandatory department blocks review readiness",
        "payload": {
            "action": "ticket.create",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000005",
            "partner_name": "Missing Reviewer Partner",
            "project_case": "PersonalDataProject",
            "created_by": "biz.user",
            "dd_status": "Pass",
            "selected_departments": ["Legal"],
            "contract_signals": ["contains_personal_data"],
        },
        "expected_workflow_status": "reviewer_selection_incomplete",
    },
    "external_partner_limited": {
        "title": "External partner sees limited blocked response",
        "payload": {
            "action": "ticket.create",
            "role": "EXTERNAL_PARTNER",
            "ticket_id": "TCK-000002",
            "partner_name": "External Co",
            "project_case": "PartnerRequest",
            "created_by": "partner.user",
            "dd_status": "Pending",
        },
        "expected_workflow_status": "blocked",
    },
    "partner_request_biz_gate": {
        "title": "Partner request starts at Biz preliminary gate",
        "payload": {
            "action": "partner.request.submit",
            "role": "EXTERNAL_PARTNER",
            "ticket_id": "TCK-000006",
            "ticket_type": "Partner Request",
            "partner_name": "External Co",
            "project_case": "PartnerQuestion",
            "created_by": "partner.user",
            "dd_status": "Pending",
        },
        "expected_workflow_status": "blocked",
    },
    "termination_planned": {
        "title": "Termination workflow is planned",
        "payload": {
            "action": "termination.create",
            "role": "BIZ_MANAGER",
            "ticket_id": "TCK-000007",
            "ticket_type": "Termination",
            "partner_name": "Closing Partner",
            "project_case": "TerminationCase",
            "created_by": "biz.manager",
            "dd_status": "Pass",
            "selected_departments": ["Legal"],
        },
        "expected_workflow_status": "ready_for_review",
    },
    "legal_admin_governance": {
        "title": "Legal admin receives full governance plan",
        "payload": {
            "action": "admin.configure",
            "role": "LEGAL_ADMIN",
            "ticket_id": "TCK-000008",
            "partner_name": "Admin Managed Partner",
            "project_case": "GovernanceSetup",
            "created_by": "legal.admin",
            "dd_status": "Pass",
            "selected_departments": ["Legal"],
        },
        "expected_workflow_status": "ready_for_review",
    },
    "counterparty_send_policy_block": {
        "title": "Counterparty send requires completed internal review",
        "payload": {
            "action": "counterparty.send",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000009",
            "partner_name": "Negotiation Partner",
            "project_case": "CounterpartySend",
            "created_by": "biz.user",
            "dd_status": "Pass",
            "selected_departments": ["Legal"],
            "internal_review_status": "In Review",
        },
        "expected_workflow_status": "blocked",
    },
    "signing_policy_block": {
        "title": "Signing requires final approval",
        "payload": {
            "action": "signing.finalize",
            "role": "LEGAL_MANAGER",
            "ticket_id": "TCK-000010",
            "partner_name": "Signing Partner",
            "project_case": "FinalSigning",
            "created_by": "legal.manager",
            "dd_status": "Pass",
            "selected_departments": ["Legal"],
            "final_approval_status": "Pending",
        },
        "expected_workflow_status": "blocked",
    },
    "override_policy_block": {
        "title": "Override requires reason and risk acceptance",
        "payload": {
            "action": "workflow.override",
            "role": "LEGAL_ADMIN",
            "ticket_id": "TCK-000011",
            "partner_name": "Override Partner",
            "project_case": "OverrideCase",
            "created_by": "legal.admin",
            "dd_status": "Pending",
            "selected_departments": ["Legal"],
        },
        "expected_workflow_status": "blocked",
    },
    "urgent_review_short_sla": {
        "title": "Urgent review uses short SLA",
        "payload": {
            "action": "ticket.create",
            "role": "BIZ_OWNER",
            "ticket_id": "TCK-000012",
            "partner_name": "Urgent Partner",
            "project_case": "UrgentReview",
            "created_by": "biz.user",
            "priority": "Urgent",
            "dd_status": "Pass",
            "selected_departments": ["Legal", "FA"],
            "contract_signals": ["contains_payment_terms"],
        },
        "expected_workflow_status": "ready_for_review",
    },
}


def list_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "scenario_id": scenario_id,
            "title": scenario["title"],
            "expected_workflow_status": scenario["expected_workflow_status"],
            "payload": deepcopy(scenario["payload"]),
        }
        for scenario_id, scenario in SCENARIOS.items()
    ]


def scenario_payload(scenario_id: str) -> dict[str, Any]:
    if scenario_id not in SCENARIOS:
        raise KeyError(f"Unknown scenario: {scenario_id}")
    return deepcopy(SCENARIOS[scenario_id]["payload"])
