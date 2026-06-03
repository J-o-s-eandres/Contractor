"""Battery de pruebas end-to-end contra oasdiff real.

Cada test crea dos specs YAML (base y candidate), ejecuta:

  1. oasdiff breaking --format json (directo) → verifica raw output
  2. contractor diff (vía oasdiff engine)       → verifica output integrado
  3. contractor diff --engine legacy            → verifica legacy (cuando aplica)
"""

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from click.testing import CliRunner
from contractor.cli import cli

FIXTURES = Path(__file__).parent / "fixtures" / "battery"
OASDIFF_RAW = True  # also test raw oasdiff CLI call


def _oasdiff_available() -> bool:
    import shutil

    return shutil.which("oasdiff") is not None


_skip_no_oasdiff = pytest.mark.skipif(
    not _oasdiff_available(),
    reason="oasdiff binary not available on this machine",
)


def _oasdiff_raw(base: str, candidate: str) -> list[dict]:
    result = subprocess.run(
        [
            "oasdiff",
            "breaking",
            "--format",
            "json",
            "--include-path-params",
            base,
            candidate,
        ],
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else []


def _contractor(base: str, candidate: str, engine: str = "oasdiff") -> dict:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "diff",
            "--base",
            base,
            "--candidate",
            candidate,
            "--format",
            "json",
            "--engine",
            engine,
        ],
    )
    assert result.exit_code in (0, 1), f"contractor error: {result.output}"
    return json.loads(result.output)


def _write_pair(name: str, base_spec: dict, candidate_spec: dict) -> tuple[str, str]:
    (FIXTURES / name).mkdir(parents=True, exist_ok=True)
    base_path = str(FIXTURES / name / "base.yaml")
    cand_path = str(FIXTURES / name / "candidate.yaml")
    for p, spec in [(base_path, base_spec), (cand_path, candidate_spec)]:
        with open(p, "w") as f:
            yaml.dump(spec, f, default_flow_style=False)
    return base_path, cand_path


_EMPTY_API = {"openapi": "3.0.0", "info": {"title": "T", "version": "1"}, "paths": {}}


# ── Tests ────────────────────────────────────────────────────────────────


@_skip_no_oasdiff
def test_identical_specs():
    """Sin cambios → exit 0, 0 breaking changes."""
    base, cand = _write_pair("identical", _EMPTY_API, _EMPTY_API)
    raw = _oasdiff_raw(base, cand)
    assert raw == []

    out = _contractor(base, cand)
    assert out["breaking"] is False
    assert out["count"] == 0


@_skip_no_oasdiff
def test_endpoint_removed():
    """DELETE /users/{id} removido sin deprecación → 1 breaking."""
    base_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/users/{id}": {
                "delete": {
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"204": {"description": "ok"}},
                }
            }
        },
    }
    base, cand = _write_pair("endpoint-removed", base_spec, _EMPTY_API)
    raw = _oasdiff_raw(base, cand)
    assert any("api-path-removed" in c["id"] for c in raw)

    out = _contractor(base, cand)
    assert out["count"] == 1
    assert "api-path-removed" in out["changes"][0]["rule_id"]
    assert out["changes"][0]["kind"] == "endpoint_removed"
    assert out["changes"][0]["method"] == "DELETE"
    assert out["changes"][0]["path"] == "/users/{id}"


@_skip_no_oasdiff
def test_type_changed():
    """Campo amount: string → number es breaking."""
    base_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/orders": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"amount": {"type": "string"}},
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "created"}},
                }
            }
        },
    }
    cand_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/orders": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"amount": {"type": "number"}},
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "created"}},
                }
            }
        },
    }
    base, cand = _write_pair("type-changed", base_spec, cand_spec)
    raw = _oasdiff_raw(base, cand)
    assert any("type-changed" in c["id"] for c in raw)

    out = _contractor(base, cand)
    assert out["count"] == 1
    assert out["changes"][0]["kind"] == "type_changed"
    assert out["changes"][0]["rule_id"] == "request-property-type-changed"


@_skip_no_oasdiff
def test_required_param_added():
    """Parámetro query opcional → required es breaking."""
    base_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "filter",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    cand_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "filter",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    base, cand = _write_pair("required-param", base_spec, cand_spec)
    raw = _oasdiff_raw(base, cand)
    assert any(c["level"] == 3 for c in raw)

    out = _contractor(base, cand)
    assert out["count"] == 1
    assert out["changes"][0]["kind"] in ("required_param_added", "other")
    assert out["changes"][0]["path"] == "/users"
    assert out["changes"][0]["method"] == "GET"


@_skip_no_oasdiff
def test_required_field_added():
    """Campo nuevo en required[] del request body es breaking."""
    base_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/orders": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["amount"],
                                    "properties": {
                                        "amount": {"type": "string"},
                                        "notes": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "created"}},
                }
            }
        },
    }
    cand_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/orders": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["amount", "notes"],
                                    "properties": {
                                        "amount": {"type": "string"},
                                        "notes": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "created"}},
                }
            }
        },
    }
    base, cand = _write_pair("required-field", base_spec, cand_spec)
    raw = _oasdiff_raw(base, cand)
    assert len(raw) == 1

    out = _contractor(base, cand)
    assert out["count"] == 1
    assert out["changes"][0]["kind"] in ("required_field_added", "other")


@_skip_no_oasdiff
def test_no_breaking_when_optional_field_added():
    """Agregar campo opcional NO es breaking change."""
    base_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"id": {"type": "string"}},
                                    }
                                },
                            },
                        }
                    },
                }
            }
        },
    }
    cand_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "name": {"type": "string"},
                                        },
                                    }
                                },
                            },
                        }
                    },
                }
            }
        },
    }
    base, cand = _write_pair("optional-field", base_spec, cand_spec)
    raw = _oasdiff_raw(base, cand)
    assert raw == []

    out = _contractor(base, cand)
    assert out["breaking"] is False
    assert out["count"] == 0


@_skip_no_oasdiff
def test_endpoint_added_is_not_breaking():
    """Agregar endpoint nuevo NO es breaking."""
    base, cand = _write_pair(
        "endpoint-added",
        _EMPTY_API,
        {
            "openapi": "3.0.0",
            "info": {"title": "T", "version": "1"},
            "paths": {
                "/health": {"get": {"responses": {"200": {"description": "ok"}}}},
            },
        },
    )
    out = _contractor(base, cand)
    assert out["breaking"] is False
    assert out["count"] == 0


@_skip_no_oasdiff
def test_enum_removed_value():
    """Remover valor de un enum es breaking."""
    base_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "status",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["active", "inactive", "archived"],
                            },
                        },
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    cand_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "status",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["active", "inactive"],
                            },
                        },
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    base, cand = _write_pair("enum-removed", base_spec, cand_spec)
    raw = _oasdiff_raw(base, cand)
    assert any("enum" in c.get("id", "") for c in raw)

    out = _contractor(base, cand)
    assert out["count"] >= 1


@_skip_no_oasdiff
def test_security_scheme_removed():
    """Remover OAuth scope es INFO level → contractor lo filtra (0 ERR)."""
    base_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "components": {
            "securitySchemes": {
                "oauth2": {
                    "type": "oauth2",
                    "flows": {
                        "implicit": {
                            "authorizationUrl": "https://example.com/auth",
                            "scopes": {"read": "read access", "write": "write access"},
                        }
                    },
                }
            }
        },
        "paths": {"/health": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    cand_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "components": {
            "securitySchemes": {
                "oauth2": {
                    "type": "oauth2",
                    "flows": {
                        "implicit": {
                            "authorizationUrl": "https://example.com/auth",
                            "scopes": {"read": "read access"},
                        }
                    },
                }
            }
        },
        "paths": {"/health": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    base, cand = _write_pair("security-removed", base_spec, cand_spec)

    # changelog lo detecta como INFO
    result = subprocess.run(
        [
            "oasdiff",
            "changelog",
            "--format",
            "json",
            "--include-path-params",
            base,
            cand,
        ],
        capture_output=True,
        text=True,
    )
    raw = json.loads(result.stdout) if result.stdout.strip() else []
    assert any("oauth-scope-removed" in c.get("id", "") for c in raw), (
        "oasdiff changelog debe detectar scope removido"
    )

    # contractor breaking NO lo reporta (INFO filtrado)
    out = _contractor(base, cand)
    assert out["count"] == 0


@_skip_no_oasdiff
def test_json_output_structure():
    """El output JSON tiene todos los campos esperados."""
    base, cand = _write_pair(
        "json-structure",
        {
            "openapi": "3.0.0",
            "info": {"title": "T", "version": "1"},
            "paths": {
                "/x": {
                    "delete": {
                        "parameters": [],
                        "responses": {"204": {"description": "ok"}},
                    }
                },
            },
        },
        _EMPTY_API,
    )
    out = _contractor(base, cand)

    assert "breaking" in out
    assert "count" in out
    assert "engine" in out
    assert out["engine"] == "oasdiff"
    assert "base" in out
    assert "candidate" in out
    assert "changes" in out

    c = out["changes"][0]
    assert "kind" in c
    assert "path" in c
    assert "method" in c
    assert "description" in c
    assert "rule_id" in c
    assert "fingerprint" in c
    assert "level" in c
    assert c["level"] == "ERR"


@_skip_no_oasdiff
def test_fingerprint_stability():
    """Mismo cambio produce mismo fingerprint (determinismo)."""
    base, cand = _write_pair(
        "fingerprint-stable",
        {
            "openapi": "3.0.0",
            "info": {"title": "T", "version": "1"},
            "paths": {
                "/x": {
                    "delete": {
                        "parameters": [],
                        "responses": {"204": {"description": "ok"}},
                    }
                },
            },
        },
        _EMPTY_API,
    )
    fp1 = _contractor(base, cand)["changes"][0]["fingerprint"]

    # Mismos specs en otra ubicación
    base2, cand2 = _write_pair(
        "fingerprint-stable-dup",
        {
            "openapi": "3.0.0",
            "info": {"title": "T", "version": "1"},
            "paths": {
                "/x": {
                    "delete": {
                        "parameters": [],
                        "responses": {"204": {"description": "ok"}},
                    }
                },
            },
        },
        _EMPTY_API,
    )
    fp2 = _contractor(base2, cand2)["changes"][0]["fingerprint"]

    assert fp1 == fp2, f"fingerprints differ: {fp1} != {fp2}"


def test_legacy_engine_still_works():
    """El flag --engine legacy sigue funcionando."""
    base, cand = _write_pair(
        "legacy-works",
        {
            "openapi": "3.0.0",
            "info": {"title": "T", "version": "1"},
            "paths": {
                "/x": {
                    "delete": {
                        "parameters": [],
                        "responses": {"204": {"description": "ok"}},
                    }
                },
            },
        },
        _EMPTY_API,
    )
    out = _contractor(base, cand, engine="legacy")
    assert out["count"] == 1
    assert out["changes"][0]["kind"] == "endpoint_removed"


@_skip_no_oasdiff
def test_oasdiff_vs_legacy_different_sensitivity():
    """oasdiff detecta cambios que legacy no detecta (enum, constraint, etc.)."""
    base_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/items": {
                "get": {
                    "parameters": [
                        {
                            "name": "size",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "minimum": 1, "maximum": 100},
                        },
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    cand_spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {
            "/items": {
                "get": {
                    "parameters": [
                        {
                            "name": "size",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "minimum": 10, "maximum": 50},
                        },
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    base, cand = _write_pair("constraint-tightened", base_spec, cand_spec)

    out_oasdiff = _contractor(base, cand, engine="oasdiff")
    out_legacy = _contractor(base, cand, engine="legacy")

    # oasdiff detecta el cambio de constraint
    assert out_oasdiff["count"] >= 1, "oasdiff should detect constraint changes"
    # legacy no lo detecta (no tiene esa capacidad)
    assert out_legacy["count"] == 0, "legacy should NOT detect constraint changes"
