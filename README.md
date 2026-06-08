<p align="right">
  <a href="README.es.md">🇪🇸 Español</a>
</p>

# Contractor

**Detect breaking changes in your OpenAPI specs before they hit production.**  
One command. No config. Zero false positives.

---

## The Problem

You renamed a field in your API response. Three services depend on it. You find out at 3 AM from a PagerDuty alert.

Contractor catches this in CI/CD, before merge. It tells you exactly what changed, where, and who needs to know.

---

## Quick Start

```bash
pip install contractor-cli

# Compare two OpenAPI specs:
```

**Requirements:** Python 3.10+ and [oasdiff](https://github.com/oasdiff/oasdiff) v1.18+ (`brew install oasdiff`)

---

## What It Detects

| Category | Example |
|----------|---------|
| 🚫 Endpoints removed | `DELETE /users/{id}` disappears |
| ⚠️ Required params added | `?filter` becomes mandatory |
| 🔀 Type changed | `amount: string` → `amount: number` |
| 📋 Required fields added | New field in request body `required[]` |
| 🔒 Enum / Constraint changes | Valid values removed, limits tightened |
| 🧩 Schema composition changed | `allOf` / `anyOf` restructured |
| 🛡️ Security scheme changes | OAuth scopes removed |
| 📅 Deprecation violations | API removed before sunset date |
| **…plus 450+ rules** via oasdiff engine | |

---

## Usage

```bash
contractor diff --base main.yaml --candidate feature.yaml
```

| Flag | Description | Default |
|------|-------------|---------|
| `--base` | Path to the baseline OpenAPI spec | required |
| `--candidate` | Path to the candidate OpenAPI spec | required |
| `--format` | Output: `console`, `json`, `markdown` | `console` |
| `--output` | Write report to file | none |
| `--engine` | Detection engine: `oasdiff` or `legacy` | `oasdiff` |

**Exit codes:** `0` = safe to merge • `1` = breaking detected • `2` = error

---

## Windows Binary

Download the standalone executable from [GitHub Releases](https://github.com/J-o-s-eandres/Contractor/releases/latest) (no Python or oasdiff needed):

```bat
contractor.exe diff --base main.yaml --candidate feature.yaml
```

---

## Build del ejecutable

Para generar un ejecutable de Windows independiente del CLI:

```bat
cd cli
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
pyinstaller contractor.spec
```

Esto generará el ejecutable en `cli/dist/contractor.exe`.

También puedes usar el script de build incluido:

```bat
cd cli
build-exe.bat
```

> Nota: el motor por defecto es `oasdiff`, que debe estar disponible en `PATH`. Si no deseas depender de `oasdiff`, ejecuta el binario con `--engine legacy`:
>
> ```bat
dist\contractor.exe diff --base main.yaml --candidate feature.yaml --engine legacy
> ```

---

>>>>>>> 593af19 (docs: add Windows Binary section, fix pip install command in READMEs)
## Output Formats

### Console (default)

Colored table via [Rich](https://github.com/Textualize/rich) — Type, Location, Description.

### JSON

```json
{
  "breaking": true,
  "count": 1,
  "changes": [
    {
      "kind": "endpoint_removed",
      "path": "/users/{id}",
      "method": "DELETE",
      "location": "base.yaml:24:5",
      "description": "api removed without deprecation"
    }
  ]
}
```

### Markdown

Markdown table for PR comments. Generate with `--format markdown --output report.md`.

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Check API contract
  run: contractor diff --base main/openapi.yaml --candidate pr/openapi.yaml
```

See full template at [`templates/github-action.yml`](cli/templates/github-action.yml).

### GitLab CI

```yaml
api-contract-check:
  script:
    - pip install contractor
    - contractor diff --base openapi/main.yaml --candidate openapi/feature.yaml --output report.md
  artifacts:
    when: on_failure
    paths: [report.md]
```

---

## Framework Support

Python · JavaScript · Java · Go · PHP · Ruby · Rust · C# · Kotlin · Elixir · Scala

Works with FastAPI, Express, Spring Boot, Gin, Laravel, Rails, Actix-Web, ASP.NET Core, Ktor, Phoenix, Play — and [25+ frameworks](docs/frameworks/README.md).

---

## How It Works

```
contractor
  └─ oasdiff (450+ detection rules)
       └─ adapter → internal model
            └─ formatters (console, json, markdown)
```

Detection powered by [oasdiff](https://github.com/oasdiff/oasdiff). We focus on team orchestration — alerts, PR comments, audit history, zero-config setup.

---

## Test Suite

✅ **236 tests** — all passing. Covers adapters, CLI, formatters, legacy engine, parser, models, and end-to-end integration.

---

## Contributing

MIT License. Contributions welcome.

See [`cli/README.md`](cli/README.md) for development setup and [`docs/detection-engine.md`](docs/detection-engine.md) for architecture details.

---

<p align="center">
  <a href="https://pypi.org/project/contractor-cli/"><img src="https://img.shields.io/pypi/v/contractor-cli" alt="PyPI"></a>
  <a href="https://github.com/J-o-s-eandres/Contractor/releases/latest"><img src="https://img.shields.io/github/v/release/J-o-s-eandres/Contractor" alt="Release"></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-236%20%E2%9C%93-brightgreen" alt="Tests"></a>
  <a href="#"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python"></a>
</p>
