from governance.schema_validation import validate_against_schema
from governance.schemas import get_schema


def test_validate_against_schema_accepts_valid_invocation_payload() -> None:
    payload = {
        "action": "ticket.create",
        "role": "BIZ_OWNER",
        "ticket_id": "TCK-VALID",
        "partner_name": "Valid Partner",
        "project_case": "ValidCase",
        "created_by": "biz.user",
    }

    assert validate_against_schema(payload, get_schema("invocation_payload")) == []


def test_validate_against_schema_reports_missing_required_field() -> None:
    payload = {
        "action": "ticket.create",
        "role": "BIZ_OWNER",
    }

    issues = validate_against_schema(payload, get_schema("invocation_payload"))

    assert "$.ticket_id: missing required field" in issues
    assert "$.partner_name: missing required field" in issues


def test_validate_against_schema_reports_enum_mismatch() -> None:
    payload = {
        "action": "ticket.delete",
        "role": "BIZ_OWNER",
        "ticket_id": "TCK-INVALID",
        "partner_name": "Invalid Partner",
        "project_case": "InvalidCase",
        "created_by": "biz.user",
    }

    issues = validate_against_schema(payload, get_schema("invocation_payload"))

    assert "$.action: value 'ticket.delete' is not in enum" in issues
