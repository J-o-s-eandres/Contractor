<p align="right">
  <a href="README.md">🇬🇧 English</a>
</p>

# Contractor

**Detecta cambios disruptivos en tus especificaciones OpenAPI antes de que lleguen a producción.**  
Un comando. Sin configuración. Cero falsos positivos.

---

## El Problema

Renombraste un campo en tu API. Tres servicios dependen de él. Te enteras a las 3 AM por una alerta de PagerDuty.

Contractor lo detecta en CI/CD, antes del merge. Te dice qué cambió, dónde, y quién necesita saberlo.

---

## Inicio Rápido

```bash
pip install contractor-cli

# Compara dos especificaciones OpenAPI:
contractor diff --base openapi-main.yaml --candidate openapi-feature.yaml
```

**Requisitos:** Python 3.10+ y [oasdiff](https://github.com/oasdiff/oasdiff) v1.18+ (`brew install oasdiff`)

---

## Qué Detecta

| Categoría | Ejemplo |
|-----------|---------|
| 🚫 Endpoints eliminados | `DELETE /users/{id}` desaparece |
| ⚠️ Parámetros requeridos agregados | `?filter` se vuelve obligatorio |
| 🔀 Tipo de campo cambiado | `amount: string` → `amount: number` |
| 📋 Campos requeridos agregados | Nuevo campo en `required[]` del body |
| 🔒 Cambios en enum / restricciones | Valores válidos eliminados, límites ajustados |
| 🧩 Composición de schema modificada | `allOf` / `anyOf` reestructurado |
| 🛡️ Cambios en esquema de seguridad | Scopes de OAuth eliminados |
| 📅 Violaciones de deprecación | API eliminada antes de la fecha de retiro |
| **…más 450+ reglas** vía motor oasdiff | |

---

## Uso

```bash
contractor diff --base main.yaml --candidate feature.yaml
```

| Flag | Descripción | Default |
|------|-------------|---------|
| `--base` | Ruta a la especificación base (main) | requerido |
| `--candidate` | Ruta a la especificación candidata (feature) | requerido |
| `--format` | Salida: `console`, `json`, `markdown` | `console` |
| `--output` | Guardar reporte en archivo | ninguno |
| `--engine` | Motor de detección: `oasdiff` o `legacy` | `oasdiff` |

**Códigos de salida:** `0` = seguro de mergear • `1` = breaking detectado • `2` = error

---

## Windows Binary

Descarga el ejecutable standalone desde [GitHub Releases](https://github.com/J-o-s-eandres/Contractor/releases/latest) (no requiere Python ni oasdiff):

```bat
contractor.exe diff --base main.yaml --candidate feature.yaml
```

---

## Formatos de Salida

### Consola (default)

Tabla coloreada vía [Rich](https://github.com/Textualize/rich) — Tipo, Ubicación, Descripción.

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

Tabla Markdown para comentarios en PRs. Generar con `--format markdown --output report.md`.

---

## Integración en CI/CD

### GitHub Actions

```yaml
- name: Check API contract
  run: contractor diff --base main/openapi.yaml --candidate pr/openapi.yaml
```

Ver template completo en [`templates/github-action.yml`](cli/templates/github-action.yml).

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

## Frameworks Soportados

Python · JavaScript · Java · Go · PHP · Ruby · Rust · C# · Kotlin · Elixir · Scala

Funciona con FastAPI, Express, Spring Boot, Gin, Laravel, Rails, Actix-Web, ASP.NET Core, Ktor, Phoenix, Play — y [25+ frameworks](docs/frameworks/README.md).

---

## Cómo Funciona

```
contractor
  └─ oasdiff (450+ reglas de detección)
       └─ adaptador → modelo interno
            └─ formateadores (console, json, markdown)
```

La detección usa [oasdiff](https://github.com/oasdiff/oasdiff). Nosotros nos enfocamos en orquestación de equipos — alertas, comentarios en PRs, historial, configuración cero.

---

## Test Suite

✅ **236 tests** — todos pasando. Cubre adaptadores, CLI, formateadores, motor legacy, parser, modelos e integración end-to-end.

---

*Contractor es gratuito y de código abierto (MIT). Las funciones Enterprise (alertas de equipo, dashboard de auditoría, SSO) están disponibles.*

---

## Contribuciones

Licencia MIT. Contribuciones bienvenidas.

Ver [`cli/README.md`](cli/README.md) para setup de desarrollo y [`docs/detection-engine.md`](docs/detection-engine.md) para detalles de arquitectura.

---

<p align="center">
  <a href="https://pypi.org/project/contractor-cli/"><img src="https://img.shields.io/pypi/v/contractor-cli" alt="PyPI"></a>
  <a href="https://github.com/J-o-s-eandres/Contractor/releases/latest"><img src="https://img.shields.io/github/v/release/J-o-s-eandres/Contractor" alt="Release"></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-236%20%E2%9C%93-brightgreen" alt="Tests"></a>
  <a href="#"><img src="https://img.shields.io/badge/license-MIT-blue" alt="Licencia"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python"></a>
</p>
