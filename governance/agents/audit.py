from datetime import datetime, timezone
from typing import Any

from governance.contracts import api_operation


def build_audit_event(
    actor: str,
    role: str,
    action: str,
    object_type: str,
    object_id: str,
    before: dict[str, Any],
    after: dict[str, Any],
    source: str,
) -> dict[str, Any]:
    return {
        "actor": actor,
        "role": role,
        "action": action,
        "object_type": object_type,
        "object_id": object_id,
        "before": before,
        "after": after,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip_address": "",
        "source": source,
    }


def build_audit_persistence_plan(
    ticket: dict[str, Any],
    audit_events: list[dict[str, Any]],
    execution_plan: dict[str, Any] | None,
) -> dict[str, Any]:
    ticket_id = ticket.get("ticket_id")
    audit_file_name = f"{ticket_id}_audit_trail.jsonl"
    execution_steps = (execution_plan or {}).get("steps", [])
    return {
        "status": "planned",
        "storage_target": "99_Audit_Trail",
        "audit_file_name": audit_file_name,
        "event_count": len(audit_events),
        "execution_step_count": len(execution_steps),
        "immutability": {
            "hard_delete_allowed": False,
            "allowed_lifecycle_actions": ["archive", "deactivate", "supersede"],
        },
        "operations": [
            api_operation(
                "POST",
                "/api/sharepoint/files/upload",
                {
                    "ticket_id": ticket_id,
                    "target_folder": "99_Audit_Trail",
                    "file_name": audit_file_name,
                    "content_type": "application/jsonl",
                    "event_count": len(audit_events),
                },
            ),
            api_operation(
                "POST",
                "/api/admin/audit-logs",
                {
                    "ticket_id": ticket_id,
                    "event_count": len(audit_events),
                    "execution_step_count": len(execution_steps),
                },
            ),
        ],
        "step_audit_links": [
            {
                "step": step["step"],
                "source_plan": step["source_plan"],
                "operation_path": step["operation"]["path"],
                "requires_audit_log": step["requires_audit_log"],
            }
            for step in execution_steps
        ],
    }
