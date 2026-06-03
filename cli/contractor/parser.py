import json
from pathlib import Path

import yaml


def load_spec(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Spec file not found: {path}")

    text = p.read_text(encoding="utf-8")

    try:
        result = yaml.safe_load(text)
        if not isinstance(result, dict):
            raise ValueError(
                f"Failed to parse OpenAPI spec: root must be a mapping, got {type(result).__name__}"
            )
        return result
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse {path}: {exc}") from exc
