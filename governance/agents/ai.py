from typing import Any

from governance.contracts import api_operation


def build_ai_plan(
    ticket: dict[str, Any],
    dd_result: dict[str, Any] | None,
    review_plan: dict[str, Any] | None,
    negotiation_plan: dict[str, Any] | None,
    termination_plan: dict[str, Any] | None,
) -> dict[str, Any]:
    operations = []

    operations.append(
        api_operation(
            "POST",
            "/api/ai/dd/analyze",
            {
                "ticket_id": ticket.get("ticket_id"),
                "partner_name": ticket.get("partner_name"),
                "tax_code": ticket.get("tax_code"),
                "dd_findings": ticket.get("dd_findings", []),
            },
        )
    )

    if dd_result:
        operations.append(
            api_operation(
                "POST",
                "/api/ai/contracts/risk-score",
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "dd_status": dd_result.get("dd_status"),
                    "risk_level": dd_result.get("risk_level"),
                    "matched_rules": dd_result.get("matched_rules", []),
                },
            )
        )

    if review_plan:
        operations.extend(
            [
                api_operation(
                    "POST",
                    "/api/ai/contracts/summarize",
                    {
                        "ticket_id": ticket.get("ticket_id"),
                        "round_id": review_plan.get("round_id"),
                        "official_file_url": ticket.get("official_file_url", ""),
                    },
                ),
                api_operation(
                    "POST",
                    "/api/ai/contracts/recommend-reviewers",
                    {
                        "ticket_id": ticket.get("ticket_id"),
                        "contract_type": review_plan.get("contract_type"),
                        "contract_signals": ticket.get("contract_signals", []),
                        "selected_departments": review_plan.get("selected_departments", []),
                    },
                ),
            ]
        )

    if negotiation_plan:
        operations.extend(
            [
                api_operation(
                    "POST",
                    "/api/ai/contracts/compare",
                    {
                        "ticket_id": ticket.get("ticket_id"),
                        "negotiation_round": negotiation_plan.get("negotiation_round"),
                        "received_file_url": ticket.get("received_file_url", ""),
                    },
                ),
                api_operation(
                    "POST",
                    "/api/ai/negotiation/playbook",
                    {
                        "ticket_id": ticket.get("ticket_id"),
                        "open_issues": negotiation_plan.get("open_issues", []),
                        "key_changes": negotiation_plan.get("key_changes", []),
                    },
                ),
            ]
        )

    if termination_plan:
        operations.append(
            api_operation(
                "POST",
                "/api/ai/termination/checklist",
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "termination_id": termination_plan.get("termination_id"),
                    "stages": termination_plan.get("stages", []),
                },
            )
        )

    return {
        "status": "planned",
        "enabled": False,
        "enablement_requirements": [
            "Configure LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL.",
            "Connect AI endpoints to document extraction, summary, compare, recommendation, and risk-score services.",
            "Store provider credentials through AgentBase Identity before production use.",
        ],
        "operations": operations,
    }
