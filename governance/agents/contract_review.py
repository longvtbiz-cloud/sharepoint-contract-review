from typing import Any


BASE_MANDATORY_DEPARTMENTS = ["Legal"]
TRIGGER_DEPARTMENT_RULES = {
    "contains_payment_terms": "FA",
    "contains_personal_data": "PDPA",
    "contains_settlement_or_reconciliation": "OPS",
    "contains_aml_or_kyc_obligation": "Compliance",
}


def prepare_contract_review(ticket: dict[str, Any], dd_result: dict[str, Any]) -> dict[str, Any]:
    if not dd_result["contract_review_allowed"]:
        return {
            "status": "Blocked",
            "block_reason": dd_result["block_reason"],
            "mandatory_departments": [],
            "missing_mandatory_departments": [],
        }

    selected = set(ticket.get("selected_departments") or [])
    signals = set(ticket.get("contract_signals") or [])
    mandatory = set(BASE_MANDATORY_DEPARTMENTS)
    triggered = []

    for signal, department in TRIGGER_DEPARTMENT_RULES.items():
        if signal in signals:
            mandatory.add(department)
            triggered.append({"condition": signal, "required_department": department})

    missing = sorted(mandatory - selected)
    return {
        "round_number": int(ticket.get("current_round", 0)) + 1,
        "round_type": "Internal Review",
        "status": "Ready" if not missing else "Reviewer Selection Incomplete",
        "selected_departments": sorted(selected),
        "mandatory_departments": sorted(mandatory),
        "missing_mandatory_departments": missing,
        "trigger_rules_applied": triggered,
        "message": (
            "This department is mandatory for this contract type and cannot be removed."
            if missing
            else "Reviewer selection satisfies the mandatory review matrix."
        ),
    }
