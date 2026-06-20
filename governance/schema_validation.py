from typing import Any


def _matches_type(value: Any, expected_type: str) -> bool:
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "null":
        return value is None
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def _format_path(path: str, child: str) -> str:
    if child.startswith("["):
        return f"{path}{child}"
    return f"{path}.{child}" if path else child


def validate_against_schema(payload: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    issues: list[str] = []

    expected_type = schema.get("type")
    if expected_type:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_matches_type(payload, item) for item in expected_types):
            issues.append(f"{path}: expected {expected_types}, got {type(payload).__name__}")
            return issues

    enum = schema.get("enum")
    if enum is not None and payload not in enum:
        issues.append(f"{path}: value {payload!r} is not in enum")

    if isinstance(payload, dict):
        for field in schema.get("required", []):
            if field not in payload:
                issues.append(f"{_format_path(path, field)}: missing required field")

        properties = schema.get("properties", {})
        for field, field_schema in properties.items():
            if field in payload:
                issues.extend(validate_against_schema(payload[field], field_schema, _format_path(path, field)))

    if isinstance(payload, list) and "items" in schema:
        for index, item in enumerate(payload):
            issues.extend(validate_against_schema(item, schema["items"], _format_path(path, f"[{index}]")))

    return issues
