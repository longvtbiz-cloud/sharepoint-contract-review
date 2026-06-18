from datetime import datetime, timezone
from typing import Any


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
