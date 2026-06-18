from typing import Any


DD_DATA_SOURCE_CATALOG = [
    {"source_name": "Business Registration", "source_type": "external_api", "stage": "DD", "priority": 1},
    {"source_name": "Tax Status", "source_type": "external_api", "stage": "DD", "priority": 2},
    {"source_name": "Licensing", "source_type": "external_api", "stage": "DD", "priority": 3},
    {"source_name": "Sanctions", "source_type": "external_api", "stage": "DD", "priority": 4},
    {"source_name": "PEP", "source_type": "external_api", "stage": "DD", "priority": 5},
    {"source_name": "Adverse Media", "source_type": "web_source", "stage": "DD", "priority": 6},
    {"source_name": "Internal DD System", "source_type": "internal_api", "stage": "DD", "priority": 7},
    {"source_name": "CRM", "source_type": "internal_api", "stage": "DD", "priority": 8},
    {"source_name": "ERP", "source_type": "internal_api", "stage": "DD", "priority": 9},
    {"source_name": "Merchant Monitoring", "source_type": "internal_api", "stage": "DD", "priority": 10},
    {"source_name": "Domain Intelligence", "source_type": "external_api", "stage": "DD", "priority": 11},
    {"source_name": "Cyber Check", "source_type": "external_api", "stage": "DD", "priority": 12},
    {"source_name": "PDPA / Data Processing Check", "source_type": "manual_upload", "stage": "DD", "priority": 13},
]

CRITICAL_FINDINGS = {
    "sanctions_match",
    "license_revoked",
    "tax_blacklisted",
}

HIGH_RISK_FINDINGS = {
    "pep_match",
    "adverse_media_high",
    "cyber_high_risk",
    "internal_watchlist",
}

CONDITIONAL_FINDINGS = {
    "license_expiring",
    "missing_pdpa_dpa",
    "tax_status_pending",
    "registration_incomplete",
}


def build_data_source_plan(ticket: dict[str, Any]) -> dict[str, Any]:
    active_sources = ticket.get("dd_sources") or DD_DATA_SOURCE_CATALOG
    operations = [
        {
            "method": "POST",
            "path": "/api/data-sources/{source_id}/sync",
            "payload": {
                "ticket_id": ticket.get("ticket_id"),
                "tax_code": ticket.get("tax_code"),
                "partner_name": ticket.get("partner_name"),
                "source_name": source["source_name"],
                "stage": "DD",
            },
            "status": "planned",
        }
        for source in sorted(active_sources, key=lambda item: item.get("priority", 999))
    ]
    return {
        "sources": active_sources,
        "operations": operations,
    }


def evaluate_rulebook(ticket: dict[str, Any]) -> dict[str, Any]:
    findings = set(ticket.get("dd_findings") or [])
    if not findings:
        return {
            "status": ticket.get("dd_status", "Pending"),
            "risk_level": "Unknown",
            "matched_rules": [],
            "required_actions": [],
        }

    critical = sorted(findings & CRITICAL_FINDINGS)
    high = sorted(findings & HIGH_RISK_FINDINGS)
    conditional = sorted(findings & CONDITIONAL_FINDINGS)

    if critical:
        status = "Reject"
        risk_level = "Critical"
        required_actions = ["Reject DD or escalate to Legal Admin for documented exception."]
    elif high:
        status = "High Risk Escalation"
        risk_level = "High"
        required_actions = ["Escalate to Compliance/Risk and require Legal Admin decision."]
    elif conditional:
        status = "Conditional Pass"
        risk_level = "Medium"
        required_actions = ["Require mitigation plan and expiry date before contract review."]
    else:
        status = "Pass"
        risk_level = "Low"
        required_actions = []

    return {
        "status": status,
        "risk_level": risk_level,
        "matched_rules": [
            *[{"finding": finding, "severity": "Critical"} for finding in critical],
            *[{"finding": finding, "severity": "High"} for finding in high],
            *[{"finding": finding, "severity": "Medium"} for finding in conditional],
        ],
        "required_actions": required_actions,
    }
