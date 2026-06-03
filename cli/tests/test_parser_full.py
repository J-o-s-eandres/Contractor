"""Full coverage tests for parser.py — JSON, BOM, comments, multi-doc, Swagger, edge cases."""

import json
import os
import tempfile

import pytest
import yaml
from contractor.parser import load_spec


def _write(content: str, suffix: str = ".yaml") -> str:
    f = tempfile.NamedTemporaryFile(
        suffix=suffix, delete=False, mode="w", encoding="utf-8"
    )
    f.write(content)
    name = f.name
    f.close()
    return name


def _valid_spec() -> dict:
    return {"openapi": "3.0.0", "info": {"title": "T", "version": "1"}, "paths": {}}


# ── File formats ──────────────────────────────────────────────────────────


def test_load_json():
    spec = _valid_spec()
    path = _write(json.dumps(spec), ".json")
    try:
        result = load_spec(path)
        assert result == spec
    finally:
        os.unlink(path)


def test_load_json_yaml_extension():
    """Cargar JSON con extensión .json, no .yaml"""
    spec = _valid_spec()
    path = _write(json.dumps(spec), ".json")
    try:
        result = load_spec(path)
        assert result["openapi"] == "3.0.0"
    finally:
        os.unlink(path)


def test_load_yaml_with_tabs_fails():
    """YAML with tabs as indentation raises error"""
    spec = _valid_spec()
    path = _write(yaml.dump(spec).replace("  ", "\t"), ".yaml")
    try:
        with pytest.raises(ValueError, match="Failed to parse"):
            load_spec(path)
    finally:
        os.unlink(path)


# ── YAML edge cases ──────────────────────────────────────────────────────


def test_yaml_with_comments():
    content = """
# This is a comment
openapi: "3.0.0"
# Another comment
info:
  title: T
  version: "1"
paths: {}
"""
    path = _write(content, ".yaml")
    try:
        result = load_spec(path)
        assert result == _valid_spec()
    finally:
        os.unlink(path)


def test_yaml_with_inline_comments():
    content = """openapi: "3.0.0"  # version
info:
  title: T  # the title
  version: "1"
paths: {}
"""
    path = _write(content, ".yaml")
    try:
        result = load_spec(path)
        assert result == _valid_spec()
    finally:
        os.unlink(path)


def test_yaml_blank_lines():
    content = """openapi: "3.0.0"


info:
  title: T
  version: "1"


paths: {}
"""
    path = _write(content, ".yaml")
    try:
        result = load_spec(path)
        assert result == _valid_spec()
    finally:
        os.unlink(path)


def test_yaml_multi_doc_raises():
    """Multi-document YAML raises ValueError wrapped ComposerError"""
    content = '---\nopenapi: "3.0.0"\ninfo: {title: T, version: "1"}\npaths: {}\n...\n---\nopenapi: "3.0.0"\ninfo: {title: X, version: "2"}\npaths: {}\n'
    path = _write(content, ".yaml")
    try:
        with pytest.raises(
            ValueError, match="Failed to parse|expected a single document"
        ):
            load_spec(path)
    finally:
        os.unlink(path)


def test_yaml_empty_dict():
    path = _write("{}", ".yaml")
    try:
        result = load_spec(path)
        assert result == {}
    finally:
        os.unlink(path)


# ── OpenAPI versions ─────────────────────────────────────────────────────


def test_openapi_3_1():
    spec = {"openapi": "3.1.0", "info": {"title": "T", "version": "1"}, "paths": {}}
    path = _write(yaml.dump(spec), ".yaml")
    try:
        result = load_spec(path)
        assert result["openapi"] == "3.1.0"
    finally:
        os.unlink(path)


def test_swagger_2_0():
    spec = {"swagger": "2.0", "info": {"title": "T", "version": "1"}, "paths": {}}
    path = _write(yaml.dump(spec), ".yaml")
    try:
        result = load_spec(path)
        assert result["swagger"] == "2.0"
    finally:
        os.unlink(path)


# ── Error cases ──────────────────────────────────────────────────────────


def test_non_dict_root():
    path = _write("- one\n- two\n- three", ".yaml")
    try:
        with pytest.raises(ValueError, match="root must be a mapping"):
            load_spec(path)
    finally:
        os.unlink(path)


def test_scalar_root():
    path = _write("hello", ".yaml")
    try:
        with pytest.raises(ValueError, match="root must be a mapping"):
            load_spec(path)
    finally:
        os.unlink(path)


def test_null_root():
    path = _write("null", ".yaml")
    try:
        with pytest.raises(ValueError, match="root must be a mapping"):
            load_spec(path)
    finally:
        os.unlink(path)


def test_nonexistent_file():
    with pytest.raises(FileNotFoundError, match="nonexistent"):
        load_spec("nonexistent_file_xyz.yaml")


def test_empty_file():
    path = _write("", ".yaml")
    try:
        with pytest.raises(ValueError, match="Failed to parse|root must be a mapping"):
            load_spec(path)
    finally:
        os.unlink(path)


def test_directory_instead_of_file(tmp_path):
    with pytest.raises((FileNotFoundError, PermissionError)):
        load_spec(str(tmp_path))


# ── Unicode ──────────────────────────────────────────────────────────────


def test_unicode_in_paths():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {"/café/{id}": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    path = _write(yaml.dump(spec, allow_unicode=True), ".yaml")
    try:
        result = load_spec(path)
        assert "/café/{id}" in result["paths"]
    finally:
        os.unlink(path)


def test_unicode_description():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "API", "version": "1"},
        "paths": {},
        "description": "Una API multilingüe — 日本語 中文 русский",
    }
    path = _write(yaml.dump(spec, allow_unicode=True), ".yaml")
    try:
        result = load_spec(path)
        assert "日本語" in result["description"]
    finally:
        os.unlink(path)


# ── Whitespace / BOM ─────────────────────────────────────────────────────


def test_file_with_bom():
    content = "\ufeff" + yaml.dump(_valid_spec())
    path = _write(content, ".yaml")
    try:
        result = load_spec(path)
        assert result == _valid_spec()
    finally:
        os.unlink(path)


def test_yaml_with_extra_whitespace():
    content = "   \n  \n" + yaml.dump(_valid_spec()) + "\n   \n"
    path = _write(content, ".yaml")
    try:
        result = load_spec(path)
        assert result == _valid_spec()
    finally:
        os.unlink(path)


def test_yaml_no_trailing_newline():
    content = yaml.dump(_valid_spec()).rstrip("\n")
    assert not content.endswith("\n")
    path = _write(content, ".yaml")
    try:
        result = load_spec(path)
        assert result == _valid_spec()
    finally:
        os.unlink(path)


# ── Large spec stress test ───────────────────────────────────────────────


def test_large_spec_performance():
    paths = {}
    for i in range(100):
        path_name = f"/api/v1/resource/{i}"
        paths[path_name] = {
            "get": {
                "parameters": [
                    {"name": f"param_{j}", "in": "query", "schema": {"type": "string"}}
                    for j in range(10)
                ],
                "responses": {"200": {"description": f"response {i}"}},
            }
        }
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Large", "version": "1"},
        "paths": paths,
    }
    path = _write(yaml.dump(spec), ".yaml")
    try:
        result = load_spec(path)
        assert len(result["paths"]) == 100
    finally:
        os.unlink(path)
