# Contractor — API Contract Testing for Engineering Teams

## What This Is

A **B2B SaaS CLI tool** that detects breaking changes in OpenAPI/Swagger API specs between microservices — and automatically alerts the teams that depend on those APIs — before a deploy reaches production.

---

## Technical Decisions

### Language: Python
- User's primary domain — fastest path to MVP
- Libraries: `click`, `rich`, `PyYAML`, `requests` (dev only)
- Binary distribution: PyInstaller (standalone binary, no Python required in CI)

### Detection Engine: oasdiff (subprocess)

**Estrategia:** No implementamos detección propia. Delegamos toda la detección de breaking changes a [oasdiff](https://github.com/oasdiff/oasdiff) vía subprocess.

```
CLI → detect.py → subprocess: oasdiff breaking --format json → oasdiff_adapter.py → BreakingChange → formatters
```

**Por qué:**
- oasdiff tiene 450+ reglas vs nuestras 4 originales
- Recibe actualizaciones gratis (nuevas reglas de OpenAPI 3.1, webhooks, etc.)
- Nosotros nos enfocamos en orquestación (equipos, notificaciones, historial)

**Engine legacy** (`--engine legacy`) mantenido como fallback con las 4 reglas originales.

### Architecture (MVP)
1. **CLI** — Python + Click + PyInstaller
   - `contractor diff --base main.yaml --candidate feature.yaml`
   - Detection via oasdiff subprocess (450+ breaking rules)
   - Outputs: exit code 0/1/2, console (Rich), JSON, Markdown
   - Fallback: `--engine legacy` (built-in, no oasdiff needed)

2. **Backend** — FastAPI + PostgreSQL + SQLAlchemy (pending)
   - Auth: email + password
   - API Keys: generated per user, hashed in DB
   - JWT: offline validation (CLI does NOT call server on every run)
   - Telemetry: opt-in only, anonymized, sanitized

3. **Frontend** — landing page + minimal dashboard
   - Bootstrap 5 + custom dark/light theme
   - EN/ES language toggle
   - "Book a Demo" modal for lead capture

### Key Architecture Decisions
- **oasdiff as subprocess**: Zero maintenance on our side for detection rules. Binary found in PATH or bundled.
- **Adapter pattern**: oasdiff JSON → internal BreakingChange model. Si cambiamos de engine, solo cambia el adapter.
- **JWT offline validation**: CLI verifies license locally using embedded public key. Server downtime never blocks customer CI/CD.
- **No cloud storage of reports**: `report.md` generated locally. Customer owns their data.
- **Self-hosted option**: Docker compose for Team/Enterprise tier.
- **API versioning**: `/api/v1/` from day 1. Never break backwards compatibility.
- **Multitenancy**: Logical (shared DB, `user_id` scoping). No per-customer infrastructure.

---

## Files

```
contractor/
├── README.md                     # GitHub repo README (EN)
├── README.es.md                  # GitHub repo README (ES)
├── CLAUDE.md                     # This file
├── docs/
│   ├── detection-engine.md       # oasdiff integration architecture
│   └── frameworks/               # Per-framework OpenAPI export guides
│       ├── README.md             # Master table (25 frameworks)
│       ├── python/
│       ├── javascript/
│       ├── java/
│       ├── go/
│       ├── php/
│       ├── ruby/
│       ├── rust/
│       ├── csharp/
│       └── extra/
└── cli/
    ├── setup.py
    ├── requirements.txt
    ├── README.md                 # CLI docs (usage, options, architecture)
    ├── templates/
    │   └── github-action.yml     # CI/CD template
    ├── contractor/
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── cli.py                # Click CLI (diff command, --engine flag)
    │   ├── detect.py             # oasdiff subprocess wrapper
    │   ├── oasdiff_adapter.py    # JSON → BreakingChange mapper
    │   ├── models.py             # BreakingChange dataclass
    │   ├── parser.py             # YAML/JSON spec loader
    │   ├── detectors/            # Legacy engine (4 built-in rules)
    │   │   ├── endpoints.py
    │   │   ├── parameters.py
    │   │   ├── types.py
    │   │   └── required.py
    │   └── formatters/
    │       ├── console.py        # Rich table output
    │       ├── json_fmt.py       # JSON output
    │       └── markdown.py       # Markdown report
    ├── tests/
    │   ├── test_cli.py           # CLI tests (exit codes, formats, --engine)
    │   ├── test_detect.py        # Subprocess mock tests
    │   ├── test_oasdiff_adapter.py # Adapter classification tests
    │   ├── test_battery.py       # 13 integration tests against real oasdiff
    │   ├── test_formatters.py    # Output format tests
    │   ├── test_models.py        # Model tests
    │   └── fixtures/
    │       ├── base.yaml         # Legacy test fixtures
    │       ├── candidate.yaml
    │       └── battery/          # Battery test fixtures (auto-generated)
    └── examples/
        └── specs/                # Example API specs for demo
```

---

## Next Steps (In Order)

1. ✅ CLI MVP built (oasdiff engine + legacy fallback)
2. ⬜ Build auth + API key backend (FastAPI)
3. ⬜ 3 beta customers using CLI in CI/CD
4. ⬜ Launch Free plan on GitHub (open source)
5. ⬜ Product Hunt launch

---

## Publishing (Internal)

### PyPI

```bash
cd cli
pip install build twine
python -m build . --outdir dist/
twine upload dist/contractor_cli-* -u __token__ -p pypi-xxxxxxxx
```

### GitHub Release

```bash
# Create release
curl -s -X POST https://api.github.com/repos/J-o-s-eandres/Contractor/releases \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"tag_name":"v0.1.0","name":"v0.1.0","body":"...","draft":false,"prerelease":false}'

# Upload binary
curl -s -X POST "https://uploads.github.com/repos/J-o-s-eandres/Contractor/releases/<id>/assets?name=contractor.exe" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"cli/dist/contractor.exe"
```
