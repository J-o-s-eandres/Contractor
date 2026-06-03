from dataclasses import dataclass, field
from typing import Literal

ChangeKind = Literal[
    "endpoint_removed",
    "required_param_added",
    "type_changed",
    "required_field_added",
    "other",
]


@dataclass(unsafe_hash=True)
class BreakingChange:
    kind: ChangeKind
    path: str  # API path, e.g. "/users/{id}"
    method: str  # HTTP method, e.g. "DELETE" — empty string for path-level
    location: (
        str  # Human location, e.g. "parameter:filter" or "body.amount" or source file
    )
    description: str  # Full human-readable sentence
    rule_id: str = ""  # oasdiff rule ID, e.g. "api-removed-without-deprecation"
    fingerprint: str = ""  # Stable hash for dedup across versions
    level: str = "ERR"  # ERR | WARN | INFO
    base_value: str = ""  # Value before the change (empty for additions)
    candidate_value: str = ""  # Value after the change (empty for removals)

    @property
    def is_breaking(self) -> bool:
        return self.level == "ERR"
