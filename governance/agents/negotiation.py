from typing import Any

from governance.contracts import api_operation


def build_negotiation_plan(ticket: dict[str, Any]) -> dict[str, Any] | None:
    action = ticket.get("action")
    ticket_type = ticket.get("ticket_type")
    if action not in {"counterparty.send", "counterparty.receive"} and ticket_type != "Partner Request":
        return None

    negotiation_round = int(ticket.get("negotiation_round", 1))
    base_payload = {
        "ticket_id": ticket.get("ticket_id"),
        "negotiation_round": negotiation_round,
        "partner_name": ticket.get("partner_name"),
    }

    operations = []
    if action == "counterparty.send":
        operations.append(
            api_operation(
                "POST",
                "/api/sharepoint/files/copy",
                {
                    **base_payload,
                    "source_file_url": ticket.get("official_file_url", ""),
                    "target_folder": "03_Counterparty_Negotiation/Sent",
                },
            )
        )
    elif action == "counterparty.receive":
        operations.extend(
            [
                api_operation(
                    "POST",
                    "/api/sharepoint/files/upload",
                    {
                        **base_payload,
                        "target_folder": "03_Counterparty_Negotiation/Received",
                        "received_file_url": ticket.get("received_file_url", ""),
                    },
                ),
                api_operation(
                    "POST",
                    "/api/contracts/rounds/create",
                    {
                        **base_payload,
                        "round_type": "Internal Review",
                        "reason": "Counterparty redline received",
                    },
                ),
            ]
        )

    return {
        "negotiation_round": negotiation_round,
        "status": "Planned",
        "decision": ticket.get("negotiation_decision", "Further Review"),
        "key_changes": ticket.get("key_changes", []),
        "open_issues": ticket.get("open_issues", []),
        "operations": operations,
    }
