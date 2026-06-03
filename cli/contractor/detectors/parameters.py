from contractor.models import BreakingChange

_HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
)


def detect_required_params_added(base: dict, candidate: dict) -> list[BreakingChange]:
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

            base_params = {
                p["name"]: p
                for p in (base_op.get("parameters") or [])
                if isinstance(p, dict) and "name" in p
            }
            candidate_params = {
                p["name"]: p
                for p in (candidate_op.get("parameters") or [])
                if isinstance(p, dict) and "name" in p
            }

            for name, c_param in candidate_params.items():
                if not c_param.get("required"):
                    continue
                b_param = base_params.get(name)

                if b_param is None:
                    changes.append(
                        BreakingChange(
                            kind="required_param_added",
                            path=path,
                            method=method.upper(),
                            location=f"parameter:{name}",
                            description=f"New required parameter '{name}' added to {method.upper()} {path}",
                            base_value="(not present)",
                            candidate_value=f"required {c_param.get('in', 'query')} parameter",
                        )
                    )
                elif not b_param.get("required"):
                    changes.append(
                        BreakingChange(
                            kind="required_param_added",
                            path=path,
                            method=method.upper(),
                            location=f"parameter:{name}",
                            description=f"Parameter '{name}' became required in {method.upper()} {path}",
                            base_value="optional",
                            candidate_value="required",
                        )
                    )

    return changes
