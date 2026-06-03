# Contractor

**Detect breaking changes in your OpenAPI specs before they hit production.**
<br>*Detecta cambios disruptivos en tus especificaciones OpenAPI antes de que lleguen a producción.*

---

## The Problem • El Problema

You renamed a field in your API response. Three services depend on it. You find out at 3 AM from a PagerDuty alert.  
*Renombraste un campo en tu API. Tres servicios dependen de él. Te enteras a las 3 AM por una alerta de PagerDuty.*

Contractor catches this in CI/CD, before merge. It tells you exactly what changed, where, and who needs to know.
*Contractor lo detecta en CI/CD, antes del merge. Te dice qué cambió, dónde, y quién necesita saberlo.*

---

## Quick Start • Inicio Rápido

```bash
pip install contractor

# Compare two OpenAPI specs:
contractor diff --base openapi-main.yaml --candidate openapi-feature.yaml
```

**Requirements:** Python 3.10+ and [oasdiff](https://github.com/oasdiff/oasdiff) v1.18+ (`brew install oasdiff`)

---

## What It Detects • Qué Detecta

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

## Usage • Uso

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

## Output Formats • Formatos de Salida

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

## CI/CD Integration • Integración en CI/CD

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

## Framework Support • Frameworks Soportados

Python · JavaScript · Java · Go · PHP · Ruby · Rust · C# · Kotlin · Elixir · Scala

Works with FastAPI, Express, Spring Boot, Gin, Laravel, Rails, Actix-Web, ASP.NET Core, Ktor, Phoenix, Play — and [25+ frameworks](docs/frameworks/README.md).

---

## How It Works • Cómo Funciona

```
contractor
  └─ oasdiff (450+ detection rules)
       └─ adapter → internal model
            └─ formatters (console, json, markdown)
```

Detection powered by [oasdiff](https://github.com/oasdiff/oasdiff). We focus on team orchestration — alerts, PR comments, audit history, zero-config setup.  
*La detección usa oasdiff. Nosotros nos enfocamos en orquestación de equipos — alertas, comentarios en PRs, historial, configuración cero.*

---

## Test Suite

✅ **236 tests** — all passing. Covers adapters, CLI, formatters, legacy engine, parser, models, and end-to-end integration.

---

## Contributing

MIT License. Contributions welcome.  
*Licencia MIT. Contribuciones bienvenidas.*

See [`cli/README.md`](cli/README.md) for development setup and [`docs/detection-engine.md`](docs/detection-engine.md) for architecture details.

---

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/tests-236%20%E2%9C%93-brightgreen" alt="Tests"></a>
  <a href="#"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python"></a>
</p>
