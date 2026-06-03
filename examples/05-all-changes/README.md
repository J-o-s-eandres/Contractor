# 05 — Todos los Cambios Combinados

Este escenario combina los 4 tipos de breaking changes en un solo par de specs. Incluye ejemplos adicionales con formatos JSON y Markdown.

## Cambios incluidos

| # | Tipo | Detalle |
|---|------|---------|
| 1 | Endpoint eliminado | `DELETE /orders/{id}` fue eliminado |
| 2 | Parámetro requerido | `?status` en `GET /orders` pasó de opcional a requerido |
| 3 | Campo requerido agregado | `email` se agregó a `required[]` en `POST /orders` |
| 4 | Tipo cambiado (scope limitado) | `total` en response: `string` → `number`. |

> **Nota:** El detector de tipos actualmente compara schemas de primer nivel y propiedades directas. El cambio `total` dentro de `items.properties` (array anidado) no se captura en esta versión MVP. Se mejorará en una versión futura.

## Comandos

### Consola (default)

```bash
cd cli/
python -m contractor diff \
  --base ../examples/05-all-changes/base.yaml \
  --candidate ../examples/05-all-changes/candidate.yaml
```

### JSON output

```bash
cd cli/
python -m contractor diff \
  --base ../examples/05-all-changes/base.yaml \
  --candidate ../examples/05-all-changes/candidate.yaml \
  --format json
```

Output:
```json
{
  "breaking": true,
  "count": 4,
  "base": "../examples/05-all-changes/base.yaml",
  "candidate": "../examples/05-all-changes/candidate.yaml",
  "changes": [
    { "kind": "endpoint_removed", "path": "/orders/{id}", ... },
    { "kind": "required_param_added", "path": "/orders", ... },
    { "kind": "type_changed", "path": "/orders", ... },
    { "kind": "required_field_added", "path": "/orders", ... }
  ]
}
```

### Markdown report

```bash
cd cli/
python -m contractor diff \
  --base ../examples/05-all-changes/base.yaml \
  --candidate ../examples/05-all-changes/candidate.yaml \
  --output report.md
```

## Exit codes

| Escenario | Exit code | Significado |
|-----------|-----------|-------------|
| `base vs candidate` | 1 | Breaking changes — revisar antes de mergear |
| `base vs base` | 0 | Sin cambios — seguro para mergear |
| Archivo inexistente | 2 | Error de uso |

```bash
# Sin cambios
python -m contractor diff \
  --base ../examples/05-all-changes/base.yaml \
  --candidate ../examples/05-all-changes/base.yaml
echo "Exit code: $?"
```
