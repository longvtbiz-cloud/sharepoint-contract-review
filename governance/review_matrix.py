from typing import Any


BASE_MANDATORY_DEPARTMENTS = ["Legal"]

CONTRACT_TYPE_MATRIX = {
    "Merchant Agreement": {
        "mandatory_departments": ["Legal", "Compliance", "OPS"],
        "conditional_departments": ["FA", "Risk", "AML", "PDPA"],
    },
    "Data Processing Agreement": {
        "mandatory_departments": ["Legal", "PDPA", "Security"],
        "conditional_departments": ["Compliance", "IT"],
    },
    "Payment Terms Amendment": {
        "mandatory_departments": ["Legal", "FA"],
        "conditional_departments": ["OPS", "Risk"],
    },
}

TRIGGER_DEPARTMENT_RULES = {
    "contains_payment_terms": "FA",
    "contains_personal_data": "PDPA",
    "contains_settlement_or_reconciliation": "OPS",
    "contains_aml_or_kyc_obligation": "Compliance",
    "contains_security_obligation": "Security",
    "contains_tax_obligation": "Tax",
    "contains_procurement_commitment": "Procurement",
}

DEPARTMENT_REVIEWER_ROLE = {
    "Legal": "LEGAL_REVIEWER",
    "Compliance": "COMPLIANCE_REVIEWER",
    "FA": "FA_REVIEWER",
    "OPS": "OPS_REVIEWER",
    "Risk": "RISK_REVIEWER",
    "Security": "SECURITY_REVIEWER",
    "PDPA": "PDPA_REVIEWER",
    "Product": "PRODUCT_REVIEWER",
    "IT": "OPS_REVIEWER",
    "Tax": "FA_REVIEWER",
    "Procurement": "OPS_REVIEWER",
    "AML": "COMPLIANCE_REVIEWER",
}


def evaluate_review_matrix(ticket: dict[str, Any]) -> dict[str, Any]:
    contract_type = ticket.get("contract_type") or "default"
    matrix = CONTRACT_TYPE_MATRIX.get(
        contract_type,
        {"mandatory_departments": BASE_MANDATORY_DEPARTMENTS, "conditional_departments": []},
    )
    selected = set(ticket.get("selected_departments") or [])
    signals = set(ticket.get("contract_signals") or [])
    mandatory = set(matrix["mandatory_departments"])
    triggered = []

    for signal, department in TRIGGER_DEPARTMENT_RULES.items():
        if signal in signals:
            mandatory.add(department)
            triggered.append({"condition": signal, "required_department": department})

    missing = sorted(mandatory - selected)
    return {
        "contract_type": contract_type,
        "selected_departments": sorted(selected),
        "mandatory_departments": sorted(mandatory),
        "optional_departments": sorted(set(matrix["conditional_departments"]) - mandatory),
        "missing_mandatory_departments": missing,
        "trigger_rules_applied": triggered,
    }


def build_reviewer_tasks(ticket: dict[str, Any], departments: list[str], round_id: str) -> list[dict[str, Any]]:
    return [
        {
            "task_id": f"TSK-{round_id}-{index:02d}",
            "round_id": round_id,
            "department": department,
            "reviewer": None,
            "reviewer_role": DEPARTMENT_REVIEWER_ROLE.get(department, "VIEW_ONLY"),
            "status": "Pending",
            "due_date": ticket.get("due_date", ""),
            "completed_at": "",
            "summary": "",
            "key_issues": [],
            "severity": "Low",
            "instructions": [
                "Review only the official SharePoint file.",
                "Use Track Changes and comments directly on the file.",
                "Do not create duplicates or delete other reviewers' comments.",
                "Complete the task only after summary and key issues are recorded.",
            ],
        }
        for index, department in enumerate(departments, start=1)
    ]
