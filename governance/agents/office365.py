from typing import Any

from governance.contracts import api_operation


GRAPH_SCOPES = [
    "User.Read.All",
    "Group.ReadWrite.All",
    "Sites.ReadWrite.All",
    "Files.ReadWrite.All",
    "Mail.Send",
]


def build_office365_plan(ticket: dict[str, Any], review_plan: dict[str, Any] | None) -> dict[str, Any]:
    reviewer_tasks = (review_plan or {}).get("reviewer_tasks", [])
    reviewer_roles = sorted({task.get("reviewer_role") for task in reviewer_tasks if task.get("reviewer_role")})
    ticket_id = ticket.get("ticket_id")

    operations = [
        api_operation(
            "GET",
            "/api/office365/users",
            {
                "roles": reviewer_roles,
                "purpose": "Resolve reviewer identities from Microsoft Entra ID.",
            },
        ),
        api_operation(
            "GET",
            "/api/office365/groups",
            {
                "departments": (review_plan or {}).get("selected_departments", []),
                "purpose": "Resolve department groups for task assignment and notifications.",
            },
        ),
    ]

    if reviewer_tasks:
        operations.extend(
            [
                api_operation(
                    "POST",
                    "/api/office365/mail/send",
                    {
                        "ticket_id": ticket_id,
                        "template": "review_tasks_assigned",
                        "task_ids": [task["task_id"] for task in reviewer_tasks],
                    },
                ),
                api_operation(
                    "POST",
                    "/api/office365/teams/notify",
                    {
                        "ticket_id": ticket_id,
                        "message_type": "review_round_created",
                        "departments": (review_plan or {}).get("selected_departments", []),
                    },
                ),
                api_operation(
                    "POST",
                    "/api/office365/calendar/reminders",
                    {
                        "ticket_id": ticket_id,
                        "due_date": ticket.get("due_date", ""),
                        "task_ids": [task["task_id"] for task in reviewer_tasks],
                    },
                ),
            ]
        )

    return {
        "provider": "Microsoft Graph",
        "tenant_id": "",
        "client_id": "",
        "client_secret": "",
        "scopes": GRAPH_SCOPES,
        "status": "inactive_until_configured",
        "connectors": [
            "User directory",
            "Groups",
            "Email notification",
            "Calendar reminder",
            "Teams notification",
            "SharePoint document library",
            "OneDrive file reference",
        ],
        "operations": operations,
    }
