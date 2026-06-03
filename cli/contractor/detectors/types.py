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


def _compare_schemas(
    base_schema: dict,
    candidate_schema: dict,
    path: str,
    method: str,
    location_prefix: str,
) -> list[BreakingChange]:
    changes: list[BreakingChange] = []

    base_type = base_schema.get("type")
    candidate_type = candidate_schema.get("type")

    if base_type and candidate_type and base_type != candidate_type:
        changes.append(
            BreakingChange(
                kind="type_changed",
                path=path,
                method=method,
                location=location_prefix,
                description=f"Field '{location_prefix}' type changed: '{base_type}' → '{candidate_type}'",
                base_value=base_type,
                candidate_value=candidate_type,
            )
        )

    base_props: dict = base_schema.get("properties") or {}
    candidate_props: dict = candidate_schema.get("properties") or {}

    for prop_name, base_prop in base_props.items():
        candidate_prop = candidate_props.get(prop_name)
        if isinstance(base_prop, dict) and isinstance(candidate_prop, dict):
            changes.extend(
                _compare_schemas(
                    base_prop,
                    candidate_prop,
                    path,
                    method,
                    f"{location_prefix}.{prop_name}",
                )
            )

    return changes


def detect_type_changes(base: dict, candidate: dict) -> list[BreakingChange]:
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
            if b_schema and c_schema:
                changes.extend(
                    _compare_schemas(b_schema, c_schema, path, method.upper(), "body")
                )

            for status, c_resp in (candidate_op.get("responses") or {}).items():
                b_resp = (base_op.get("responses") or {}).get(status) or {}
                b_schema = _extract_schema(b_resp)
                c_schema = _extract_schema(c_resp if isinstance(c_resp, dict) else {})
                if b_schema and c_schema:
                    changes.extend(
                        _compare_schemas(
                            b_schema,
                            c_schema,
                            path,
                            method.upper(),
                            f"response.{status}",
                        )
                    )

    return changes
