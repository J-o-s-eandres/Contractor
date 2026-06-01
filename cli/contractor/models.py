from dataclasses import dataclass, field
from typing import Literal

ChangeKind = Literal[
    "endpoint_removed",
    "required_param_added",
    "type_changed",
    "required_field_added",
]


@dataclass
class BreakingChange:
    kind: ChangeKind
    path: str          # API path, e.g. "/users/{id}"
    method: str        # HTTP method, e.g. "DELETE" — empty string for path-level
    location: str      # Human location, e.g. "parameter:filter" or "body.amount"
    description: str   # Full human-readable sentence
    base_value: str    # Value before the change (empty for additions)
    candidate_value: str  # Value after the change (empty for removals)

    @property
    def is_breaking(self) -> bool:
        return True  # all instances in this MVP are breaking; reserved for future warn-only mode
