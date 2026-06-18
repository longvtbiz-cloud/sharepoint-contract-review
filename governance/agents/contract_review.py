from typing import Any

from governance.contracts import api_operation
from governance.review_matrix import build_reviewer_tasks, evaluate_review_matrix


def prepare_contract_review(ticket: dict[str, Any], dd_result: dict[str, Any]) -> dict[str, Any]:
    if not dd_result["contract_review_allowed"]:
        return {
            "status": "Blocked",
            "block_reason": dd_result["block_reason"],
            "mandatory_departments": [],
            "missing_mandatory_departments": [],
        }

    matrix_result = evaluate_review_matrix(ticket)
    missing = matrix_result["missing_mandatory_departments"]
    round_number = int(ticket.get("current_round", 0)) + 1
    round_id = f"RND-{ticket.get('ticket_id', 'TCK-DRAFT')}-{round_number:02d}"
    departments_for_tasks = sorted(set(matrix_result["selected_departments"]) | set(matrix_result["mandatory_departments"]))
    tasks = build_reviewer_tasks(ticket, departments_for_tasks, round_id)
    return {
        "round_id": round_id,
        "ticket_id": ticket.get("ticket_id"),
        "round_number": round_number,
        "round_type": "Internal Review",
        "status": "Ready" if not missing else "Reviewer Selection Incomplete",
        "contract_type": matrix_result["contract_type"],
        "selected_departments": matrix_result["selected_departments"],
        "mandatory_departments": matrix_result["mandatory_departments"],
        "optional_departments": matrix_result["optional_departments"],
        "missing_mandatory_departments": missing,
        "trigger_rules_applied": matrix_result["trigger_rules_applied"],
        "reviewer_tasks": tasks,
        "operations": [
            api_operation(
                "POST",
                "/api/contracts/rounds/create",
                {
                    "round_id": round_id,
                    "ticket_id": ticket.get("ticket_id"),
                    "round_number": round_number,
                    "round_type": "Internal Review",
                    "selected_departments": matrix_result["selected_departments"],
                    "mandatory_departments": matrix_result["mandatory_departments"],
                },
            ),
            api_operation(
                "POST",
                "/api/contracts/rounds/{round_id}/assign-reviewers",
                {
                    "round_id": round_id,
                    "tasks": tasks,
                },
            ),
        ],
        "message": (
            "This department is mandatory for this contract type and cannot be removed."
            if missing
            else "Reviewer selection satisfies the mandatory review matrix."
        ),
    }
