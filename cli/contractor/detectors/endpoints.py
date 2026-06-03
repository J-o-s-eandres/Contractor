from contractor.models import BreakingChange

_HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
)


def detect_removed_endpoints(base: dict, candidate: dict) -> list[BreakingChange]:
    changes: list[BreakingChange] = []
    base_paths: dict = base.get("paths") or {}
    candidate_paths: dict = candidate.get("paths") or {}

    for path, base_methods in base_paths.items():
        if not isinstance(base_methods, dict):
            continue
        candidate_methods: dict = candidate_paths.get(path) or {}

        for method in _HTTP_METHODS:
            if method in base_methods and method not in candidate_methods:
                changes.append(
                    BreakingChange(
                        kind="endpoint_removed",
                        path=path,
                        method=method.upper(),
                        location=f"{method.upper()} {path}",
                        description=f"Endpoint {method.upper()} {path} was removed",
                        base_value=f"{method.upper()} {path}",
                        candidate_value="",
                    )
                )

    return changes
