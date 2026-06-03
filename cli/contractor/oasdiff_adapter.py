from contractor.models import BreakingChange, ChangeKind

_KNOWN_KINDS: dict[str, ChangeKind] = {
    "api-removed": "endpoint_removed",
    "api-path-removed": "endpoint_removed",
    "request-body-removed": "endpoint_removed",
    "request-property-type-changed": "type_changed",
    "request-parameter-type-changed": "type_changed",
    "response-property-type-changed": "type_changed",
    "response-parameter-type-changed": "type_changed",
    "new-required-request-header-property": "required_field_added",
    "request-body-required-value-updated": "required_field_added",
    "new-request-non-path-parameter": "required_param_added",
    "request-parameter-required-value-updated": "required_param_added",
    "new-required-request-body": "required_field_added",
    "request-body-became-enum": "type_changed",
    "request-parameter-became-enum": "type_changed",
    "request-property-became-enum": "type_changed",
}

_LEVEL_MAP = {3: "ERR", 2: "WARN", 1: "INFO"}


def _classify(rule_id: str) -> ChangeKind:
    for key, kind in _KNOWN_KINDS.items():
        if key in rule_id:
            return kind
    return "other"


def adapt_changes(raw_changes: list[dict]) -> list[BreakingChange]:
    result: list[BreakingChange] = []
    for c in raw_changes:
        level = _LEVEL_MAP.get(c.get("level", 0), "INFO")
        if level != "ERR":
            continue

        rule_id = c.get("id", "")
        description = c.get("text", "")

        result.append(
            BreakingChange(
                kind=_classify(rule_id),
                path=c.get("path", ""),
                method=c.get("operation", ""),
                location=c.get("source", ""),
                description=description,
                rule_id=rule_id,
                fingerprint=c.get("fingerprint") or "",
                level=level,
            )
        )
    return result
