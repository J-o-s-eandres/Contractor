from contractor.models import BreakingChange
from contractor.detectors.endpoints import detect_removed_endpoints
from contractor.detectors.parameters import detect_required_params_added
from contractor.detectors.types import detect_type_changes
from contractor.detectors.required import detect_required_fields_added


def run_all(
    base: dict,
    candidate: dict,
    engine: str = "oasdiff",
    base_path: str = "",
    candidate_path: str = "",
) -> list[BreakingChange]:
    if engine == "oasdiff":
        from contractor.detect import run_oasdiff

        b = base_path or "base.yaml"
        c = candidate_path or "candidate.yaml"
        changes, _ = run_oasdiff(b, c)
        return changes

    return [
        *detect_removed_endpoints(base, candidate),
        *detect_required_params_added(base, candidate),
        *detect_type_changes(base, candidate),
        *detect_required_fields_added(base, candidate),
    ]
