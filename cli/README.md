# Contractor CLI

Detect breaking changes in your API contracts before they hit production.

Powered by [oasdiff](https://github.com/oasdiff/oasdiff) — 450+ breaking change rules.

## Installation

### Binary (recommended — no Python needed)

Download from [GitHub Releases](https://github.com/your-org/contractor/releases).

### pip

```bash
pip install contractor
```

## Requirements

**oasdiff** v1.18+ is required. Install it with one of:

```bash
brew install oasdiff                                           # macOS
go install github.com/oasdiff/oasdiff@latest                   # Go users
# Linux:
curl -sSL https://github.com/oasdiff/oasdiff/releases/latest/download/oasdiff-linux -o /usr/local/bin/oasdiff && chmod +x /usr/local/bin/oasdiff
# Windows: download oasdiff_<version>_windows_amd64.tar.gz from https://github.com/oasdiff/oasdiff/releases
```

See [oasdiff installation docs](https://github.com/oasdiff/oasdiff#installation) for Docker, apk, deb, rpm.

## Usage

```bash
contractor diff --base main/openapi.yaml --candidate feature/openapi.yaml
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--base` | Path to the baseline OpenAPI spec | required |
| `--candidate` | Path to the candidate OpenAPI spec | required |
| `--format` | Output format: `console`, `json`, `markdown` | `console` |
| `--output` | Write a Markdown report to this file | none |
| `--engine` | Detection engine: `oasdiff` or `legacy` | `oasdiff` |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | No breaking changes — safe to merge |
| `1` | Breaking changes detected — review required |
| `2` | Usage error (file not found, invalid flag, oasdiff not found) |

## What we detect

450+ breaking change rules across 12 categories:

| Category | Examples |
|----------|----------|
| Endpoints removed | `DELETE /users/{id}` removed without deprecation |
| Required params added | `?filter=` changed from optional to required |
| Type changes | `amount: string` → `amount: number` |
| Required fields added | `notes` added to `required[]` in request body |
| Enum changes | Enum value added/removed/changed |
| Const changes | `const` value modified |
| AllOf/AnyOf changes | Composition schema restructured |
| Min/Max changes | Constraint tightened |
| Pattern added | New regex validation on a parameter |
| Default value changed | `default:` modified |
| Security scheme changes | OAuth scopes removed |
| Deprecation & sunset | API removed before sunset date |

## Output formats

### Console (default)

Colored table via [Rich](https://github.com/Textualize/rich) showing Type, Location, and Description.

### JSON

```json
{
  "breaking": true,
  "count": 1,
  "base": "base.yaml",
  "candidate": "feature.yaml",
  "engine": "oasdiff",
  "changes": [
    {
      "kind": "endpoint_removed",
      "path": "/users/{id}",
      "method": "DELETE",
      "location": "base.yaml:24:5",
      "description": "api removed without deprecation",
      "rule_id": "api-path-removed-without-deprecation",
      "fingerprint": "a1059bc287bd",
      "level": "ERR"
    }
  ]
}
```

### Markdown

Markdown table with Type, Location, Description columns. Can be written to a file with `--output report.md` for PR comments.

## Detection engine

By default Contractor delegates all detection to **oasdiff** as a subprocess:

```
contractor
  └─ detect.py              ← subprocess: oasdiff breaking --format json
       └─ oasdiff_adapter.py ← mapea JSON oasdiff → modelo BreakingChange
            └─ formatters/   ← console, json, markdown (sin cambios)
```

### Engine: `oasdiff` (default)

- Calls `oasdiff breaking --format json --include-path-params --fail-on ERR`
- Returns only ERR-level changes (WARN/INFO are filtered)
- Each change includes `rule_id`, `fingerprint` (SHA256), `level`, and `source`

### Engine: `legacy` (fallback)

- Built-in Python detection (4 rules: endpoint removed, required param, type changed, required field)
- No oasdiff dependency
- Use with `--engine legacy` when oasdiff is unavailable

Both engines produce the same `BreakingChange` model, so all formatters work identically.

## Architecture

```
CLI (cli.py)
  ├── parser.py             ← carga YAML/JSON specs
  ├── detect.py             ← subprocess wrapper around oasdiff
  ├── oasdiff_adapter.py    ← mapea output oasdiff a BreakingChange
  ├── detectors/            ← engine "legacy" (4 reglas built-in)
  └── formatters/           ← console, json, markdown
```

### File reference

| File | Purpose |
|------|---------|
| `cli.py` | Click CLI, `diff` command with `--engine` flag |
| `detect.py` | `run_oasdiff()` — busca binary, ejecuta subprocess, retorna cambios |
| `oasdiff_adapter.py` | `adapt_changes()` — mapea rule IDs a ChangeKind, filtra por nivel |
| `models.py` | `BreakingChange` dataclass con `rule_id`, `fingerprint`, `level` |
| `detectors/` | Engine legacy (deprecated, mantenido por compatibilidad) |
| `formatters/` | Console (Rich), JSON, Markdown |

### Data flow

```
1. usuario: contractor diff --base base.yaml --candidate feature.yaml
2. cli.py recibe paths
3. detect.py:
   a. Busca oasdiff en PATH → bundled
   b. Ejecuta: oasdiff breaking --format json --fail-on ERR \
        --include-path-params base.yaml feature.yaml
   c. Lee stdout JSON
4. oasdiff_adapter.py:
   a. Filtra cambios con level < 3 (solo ERR)
   b. Clasifica rule_id → ChangeKind (endpoint_removed, type_changed, etc.)
   c. Retorna list[BreakingChange]
5. Formatters: renderizan según --format
6. Exit: 0 si no hay cambios, 1 si hay breaking, 2 si error
```

## CI/CD Integration

### GitHub Actions

Copy [`templates/github-action.yml`](templates/github-action.yml) to `.github/workflows/contractor.yml`.
Includes oasdiff installation step.

### GitLab CI

```yaml
api-contract-check:
  script:
    - # install oasdiff
    - apt-get update && apt-get install -y curl
    - curl -sSL https://github.com/oasdiff/oasdiff/releases/latest/download/oasdiff-linux -o /usr/local/bin/oasdiff
    - chmod +x /usr/local/bin/oasdiff
    - pip install contractor
    - contractor diff --base openapi/main.yaml --candidate openapi/feature.yaml --output report.md
  artifacts:
    when: on_failure
    paths: [report.md]
```

## Test suite

```bash
cd cli
python -m pytest tests/ -v
```

236 tests covering:

| Area | Tests | What's covered |
|------|-------|---------------|
| Adapter | 28 | Every rule ID mapping, level filtering, edge cases, fingerprints |
| CLI | 25 | All flags, formats, output files, engines, mocking, error paths |
| Formatters | 22 | Console/JSON/Markdown, all change kinds, grammar, edge cases |
| Legacy engine | 37 | Endpoints/params/types/required detectors, parametrized methods |
| Parser | 27 | JSON, YAML, BOM, comments, multi-doc, 3.1, Swagger 2.0, unicode |
| Models | 22 | Equality, hash, serialization, all level/kind variants |
| Detect subprocess | 5 | Subprocess mocking, binary search, flag passthrough |
| Battery (integration) | 13 | Full pipeline with real oasdiff binary |

## License

MIT
