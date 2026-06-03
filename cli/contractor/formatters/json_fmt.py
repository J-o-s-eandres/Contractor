import json
from dataclasses import asdict
from contractor.models import BreakingChange


def to_json(changes: list[BreakingChange], base_path: str, candidate_path: str) -> str:
    return json.dumps(
        {
            "breaking": len(changes) > 0,
            "count": len(changes),
            "base": base_path,
            "candidate": candidate_path,
            "changes": [asdict(c) for c in changes],
        },
        indent=2,
    )
