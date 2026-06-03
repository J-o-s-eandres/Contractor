# Detection Engine

> Cómo Contractor detecta breaking changes usando oasdiff como engine subprocess.

## Overview

Contractor no implementa su propio parser de OpenAPI ni sus propias reglas de detección de breaking changes. En su lugar, delega toda la detección a [oasdiff](https://github.com/oasdiff/oasdiff), la herramienta open-source más completa para comparación de specs OpenAPI.

## Arquitectura

```
┌──────────────────────────────────────────────────────┐
│                    contractor diff                    │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │ cli.py    │──▶│ detect.py│──▶│ oasdiff_adapter  │ │
│  │ (Click)   │   │(subproc) │   │ (mapeo JSON)     │ │
│  └──────────┘   └────┬─────┘   └────────┬─────────┘ │
│                       │                  │           │
│                       ▼                  ▼           │
│                ┌──────────────┐   ┌──────────────┐   │
│                │ oasdiff      │   │ BreakingChange│   │
│                │ breaking     │   │ model        │   │
│                │ --format json│   │              │   │
│                └──────────────┘   └──────┬───────┘   │
│                                          │           │
│                                          ▼           │
│                                  ┌──────────────┐   │
│                                  │ formatters/   │   │
│                                  │ console/json  │   │
│                                  │ markdown      │   │
│                                  └──────────────┘   │
└──────────────────────────────────────────────────────┘
```

## Capas

### 1. detect.py — Subprocess wrapper

Busca el binary `oasdiff` en:
1. `PATH` del sistema
2. Bundled junto al binary de Contractor (`sys.argv[0]`)

Ejecuta:

```bash
oasdiff breaking --format json --fail-on ERR --include-path-params base.yaml candidate.yaml
```

Interpreta exit codes:
- `0`: Sin cambios breaking
- `1`: Cambios breaking detectados
- `>=2`: Error real (spec inválido, archivo no encontrado, etc.)

### 2. oasdiff_adapter.py — Mapeo JSON → BreakingChange

Recibe el JSON de oasdiff y produce `list[BreakingChange]`.

**Filtrado por nivel:**

| Nivel oasdiff | Mapeo Contractor | Incluido? |
|---------------|-----------------|-----------|
| `3` (ERR)     | `"ERR"`         | Sí        |
| `2` (WARN)    | `"WARN"`        | No        |
| `1` (INFO)    | `"INFO"`        | No        |

**Clasificación de rule_ids:**

| Rule ID (oasdiff) | ChangeKind (Contractor) |
|-------------------|------------------------|
| `api-path-removed-without-deprecation` | `endpoint_removed` |
| `api-removed-without-deprecation` | `endpoint_removed` |
| `request-body-removed` | `endpoint_removed` |
| `request-property-type-changed` | `type_changed` |
| `request-parameter-type-changed` | `type_changed` |
| `response-property-type-changed` | `type_changed` |
| `new-required-request-header-property` | `required_field_added` |
| `request-body-required-value-updated` | `required_field_added` |
| `new-required-request-body` | `required_field_added` |
| `new-request-non-path-parameter` | `required_param_added` |
| `request-parameter-required-value-updated` | `required_param_added` |
| `request-parameter-became-required` | `required_param_added` |
| `request-body-became-enum` | `type_changed` |
| `request-parameter-became-enum` | `type_changed` |
| `request-property-became-enum` | `type_changed` |
| *otros* | `other` |

### 3. models.py — BreakingChange

```python
@dataclass
class BreakingChange:
    kind: str            # ChangeKind: endpoint_removed, type_changed, etc.
    path: str            # "/users/{id}"
    method: str          # "GET", "POST", etc.
    location: str        # "base.yaml:24:5" or "body.amount"
    description: str     # Human-readable sentence
    rule_id: str = ""    # "api-path-removed-without-deprecation"
    fingerprint: str = ""  # SHA256[:12] — estable entre commits
    level: str = "ERR"   # "ERR" | "WARN" | "INFO"
```

## Fingerprint

El fingerprint es un hash SHA256[:12] de `rule_id:method:path:args`. Es:
- **Estable**: mismo cambio siempre produce el mismo fingerprint
- **Útil para**: deduplicación entre commits, tracking histórico, review state
- **Generado por**: oasdiff (`formatters/changes.go:ComputeFingerprint`)

## Engine Legacy

El engine `--engine legacy` usa los detectores Python originales:

| Detector | Regla |
|----------|-------|
| `detectors/endpoints.py` | Endpoints eliminados |
| `detectors/parameters.py` | Parámetros que se volvieron required |
| `detectors/types.py` | Tipos de campos cambiados |
| `detectors/required.py` | Campos agregados a `required[]` |

Mantenido solo como fallback. No recibe nuevas funcionalidades.

## Cobertura de detección

### oasdiff engine (450+ reglas)

- Endpoints añadidos/eliminados (con deprecation awareness)
- Parámetros: tipo, required, enum, const, min/max, pattern, default
- Request/response bodies: esquemas, propiedades, tipos, required
- Security schemes: OAuth scopes, API keys, tipos
- Components: schemas, responses, parameters
- Webhooks
- Deprecation y sunset dates
- Stability levels (draft/alpha/beta/stable)

### Legacy engine (4 reglas)

- Endpoints eliminados
- Parámetros required añadidos
- Tipos de campos cambiados
- Campos required añadidos

## Testing

### Unit tests (mock)

```bash
python -m pytest tests/test_detect.py tests/test_oasdiff_adapter.py -v
```

### Integration tests (real oasdiff)

```bash
python -m pytest tests/test_battery.py -v
```

Los tests de batería crean fixtures YAML temporales, ejecutan oasdiff real, y verifican:
- Exit codes correctos (0, 1, 2)
- Cantidad de cambios esperados
- rule_id y kind correctos
- Fingerprint estable
- Output JSON completo
- Ambos engines (oasdiff y legacy)

### Fixtures de batería

Cada test en `test_battery.py` crea su propio par base/candidate en `tests/fixtures/battery/<test-name>/`:

| Test | base → candidate | Cambios esperados |
|------|-----------------|-------------------|
| `identical_specs` | specs idénticos | 0 |
| `endpoint_removed` | DELETE endpoint → vacío | 1 (endpoint_removed) |
| `type_changed` | string → number | 1 (type_changed) |
| `required_param_added` | opcional → required | 1 (required_param_added) |
| `required_field_added` | campo optional → required[] | 1 (required_field_added) |
| `enum_removed_value` | 3 valores → 1 valor | 1+ (other) |
| `optional_field_added` | spec → +campo opcional | 0 |
| `endpoint_added` | vacío → +endpoint | 0 |
| `constraint_tightened` | min=1 max=100 → min=10 max=50 | 1+ (other) |
| `security_removed` | OAuth scope write → removido | 0 (INFO level, filtrado) |
