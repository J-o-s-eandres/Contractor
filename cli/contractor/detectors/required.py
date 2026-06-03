from contractor.models import BreakingChange

_HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
)


def _extract_schema(obj: dict | None) -> dict | None:
    if not obj:
        return None
    content: dict = obj.get("content") or {}
    for media_obj in content.values():
        if isinstance(media_obj, dict) and "schema" in media_obj:
            return media_obj["schema"]
    return None


def _find_newly_required(
    base_schema: dict | None,
    candidate_schema: dict | None,
    path: str,
    method: str,
    location_prefix: str,
) -> list[BreakingChange]:
    changes: list[BreakingChange] = []
    if not base_schema or not candidate_schema:
        return changes

    base_required = set(base_schema.get("required") or [])
    candidate_required = set(candidate_schema.get("required") or [])
    newly_required = candidate_required - base_required

    for field in sorted(newly_required):
        changes.append(
            BreakingChange(
                kind="required_field_added",
                path=path,
                method=method,
                location=f"{location_prefix}.{field}",
                description=f"Field '{field}' is now required in {location_prefix} of {method} {path}",
                base_value="optional",
                candidate_value="required",
            )
        )

    return changes


def detect_required_fields_added(base: dict, candidate: dict) -> list[BreakingChange]:
    changes: list[BreakingChange] = []
    base_paths: dict = base.get("paths") or {}
    candidate_paths: dict = candidate.get("paths") or {}

    for path, candidate_methods in candidate_paths.items():
        if not isinstance(candidate_methods, dict):
            continue
        base_methods: dict = base_paths.get(path) or {}

        for method in _HTTP_METHODS:
            if method not in candidate_methods:
                continue
            base_op: dict = base_methods.get(method) or {}
            candidate_op: dict = candidate_methods[method] or {}

            b_schema = _extract_schema(base_op.get("requestBody"))
            c_schema = _extract_schema(candidate_op.get("requestBody"))
            changes.extend(
                _find_newly_required(b_schema, c_schema, path, method.upper(), "body")
            )

            for status, c_resp in (candidate_op.get("responses") or {}).items():
                b_resp = (base_op.get("responses") or {}).get(status) or {}
                b_schema = _extract_schema(b_resp)
                c_schema = _extract_schema(c_resp if isinstance(c_resp, dict) else {})
                changes.extend(
                    _find_newly_required(
                        b_schema, c_schema, path, method.upper(), f"response.{status}"
                    )
                )

    return changes
