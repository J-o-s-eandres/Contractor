# Contractor — Examples

Colección de escenarios de prueba para el CLI de Contractor. Cada carpeta contiene un par de specs OpenAPI (`base.yaml` / `candidate.yaml`) que ilustran un tipo específico de breaking change.

## Cómo usar

```bash
cd cli/
python -m contractor diff \
  --base ../examples/01-endpoint-removed/base.yaml \
  --candidate ../examples/01-endpoint-removed/candidate.yaml
```

## Escenarios

| #  | Escenario | Cambio |
|----|-----------|--------|
| 01 | Endpoint eliminado | `DELETE /users/{id}` existe en base, desaparece en candidate |
| 02 | Parámetro requerido agregado | `?filter` cambia de opcional a requerido |
| 03 | Tipo de campo cambiado | `amount: string` → `amount: number` |
| 04 | Campo requerido agregado | `tax_id` se agrega a `required[]` |
| 05 | Todos combinados | Los 4 cambios juntos, con formatos JSON y Markdown |

## Salidas disponibles

- **Console** (default): tabla coloreada en terminal
- **JSON**: `--format json` — ideal para pipelines CI
- **Markdown**: `--format markdown` o `--output report.md`
