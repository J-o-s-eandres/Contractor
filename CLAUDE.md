# Contractor — API Contract Testing for Engineering Teams

## What This Is

A **B2B SaaS CLI tool** that detects breaking changes in OpenAPI/Swagger API specs between microservices — and automatically alerts the teams that depend on those APIs — before a deploy reaches production.

**Current stage:** Pre-product. Landing page live for lead validation (demo bookings).

---

## Business Context

### The Problem
In companies with 5+ microservices, teams frequently break each other's APIs without realizing it. A field renamed, a type changed, an endpoint removed — these "small refactors" cause production incidents, rollbacks, and hours of cross-team debugging. The current solutions are:
- Manual: Slack messages, Notion docs (always outdated)
- Free CLI: `oasdiff` (detects changes but has no team notification, no PR integration, no history)
- Enterprise: PactFlow ($10k–50k/year, complex to set up)

### Our Position
**Mid-market gap:** Simple enough for a solo dev to set up in 2 minutes, powerful enough for a 20-service engineering org. We sit between oasdiff (free but limited) and PactFlow (expensive and complex).

### Why Pay vs. oasdiff (Free)?
oasdiff detects WHAT broke. Contractor tells your TEAM:
- Auto PR comment tagging affected teams
- Slack/Teams alerts sent automatically
- Team impact mapping (who depends on what)
- Audit history dashboard (compliance, postmortems)
- Zero-config (one line in CI/CD, no YAML wrangling)

---

## Target Market

**Primary ICP (Ideal Customer Profile):**
- Engineering Directors / VPs of Engineering
- Companies: 50–500 employees
- Architecture: 5–50 microservices
- Sectors: Fintech, e-commerce, SaaS B2B
- Pain signal: hiring for DevOps/SRE + Backend + "API" in job descriptions

**Secondary ICP (developer-led adoption):**
- Staff Engineers / Tech Leads
- Already know oasdiff or have a custom script
- Frustrated that "the tool works but nobody checks it"

---

## Pricing

| Plan | Price | Target |
|------|-------|--------|
| Free | $0 | Solo devs, OSS projects — acquisition funnel |
| Pro | $199/mo | Teams with 5–20 microservices |
| Team | $499/mo | Orgs with 20+ services, multiple teams |
| Enterprise | Custom | Self-hosted + SLA + compliance |

**Key insight:** $199/mo is below the "manager approval threshold" in most companies — Engineering Managers can approve it without procurement.

---

## Competitive Landscape

| Competitor | Price | Weakness |
|------------|-------|---------|
| oasdiff | Free | No team features, no PR integration, no history |
| Bump.sh (Optic) | Freemium | Documentation-focused, not CI/CD-native |
| PactFlow | $10k–50k/yr | Too complex, too expensive for mid-market |
| Homemade scripts | Dev time | Breaks on rotation, no maintenance |

**Why Optic failed:** Free tier too generous, enterprise sales cycle too long for a solo founder without capital.

---

## Go-To-Market Strategy

### Phase 1 — Validation (NOW: June 2026)
Goal: 10 demo bookings from the landing page within 30 days.
- Landing page live at `/index.html` with "Book a Demo" CTA
- Content: LinkedIn posts about the problem (not selling the product)
- Communities: CNCF Slack, r/devops, Platform Engineering Slack

### Phase 2 — Beta (July–August 2026)
Goal: 3 companies using the CLI in their CI/CD.
- CLI MVP built in Python (user's domain) + PyInstaller binary
- 0 cost for beta users
- Weekly feedback calls

### Phase 3 — Revenue (September 2026+)
Goal: $2k–5k MRR by month 6.
- Launch Free plan (open source)
- Launch Pro plan ($199/mo) with PR comments + Slack alerts
- Publish on GitHub, Product Hunt, Hacker News

### Honest MRR Projections (Conservative)
| Month | MRR |
|-------|-----|
| 3 | $0–500 |
| 6 | $1k–5k |
| 12 | $5k–15k |
| 18 | $10k–30k |

$50k MRR in 18 months is top 1% — achievable but requires everything to go right.

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

3. **Frontend** — landing page (`index.html`) + minimal dashboard
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

## DB Schema (Minimal)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    plan TEXT DEFAULT 'free', -- free | pro | team
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    key_hash TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

CREATE TABLE usage_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    date DATE NOT NULL,
    checks_run INT DEFAULT 0
);
```

---

## Content Strategy (Why Pay vs. Free)

### LinkedIn Post Formula
1. Tell a story of a painful production incident (breaking change)
2. Show how they solved it manually (slow, fragile)
3. "Here's the 1-line fix we use now" → Contractor
4. CTA: "Link in comments" → landing page

### Post topics backlog
- "We had 3 breaking changes last sprint. Here's how we caught 0 of them before production."
- "oasdiff is free and great. Here's why we still pay for Contractor."
- "The 2 AM Zoom call nobody wants to be on. And how to never have it again."
- "What actually happens when you change `string` to `number` in your API."

---

## Communities to Join (Immediately)

**Slack:**
- CNCF Slack → `slack.cncf.io` (#platform-engineering, #api-management)
- Kubernetes Slack → `slack.k8s.io`
- Platform Engineering → `platformengineering.org`
- DevOps Loop → search Google

**Reddit:**
- r/devops (1.2M)
- r/microservices
- r/ExperiencedDevs
- r/SaaS

**Discord:**
- The Programmer's Hangout
- Developer Way Discord

**Rule:** Give value for 2 weeks before any self-promotion.

---

## Validation Metrics (30-day targets)

| Metric | Target | Meaning |
|--------|--------|---------|
| Demo requests | 10 | Basic market interest |
| Demo completion rate | 60%+ | Real pain, not just curiosity |
| "Would pay $199/mo" | 50%+ of demos | Pricing validated |
| Beta signups | 3 companies | Real early adopters |

**Go/No-Go criteria:** If <5 demo requests in 30 days → revisit positioning. If 0 express willingness to pay → pivot pricing or ICP.

---

## Files

```
contractor/
├── index.html                    # Landing page (dark/light + EN/ES)
├── README.md                     # GitHub repo README (EN)
├── README.es.md                  # GitHub repo README (ES)
├── CLAUDE.md                     # This file
├── .claude/                      # Claude Code config
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

1. ✅ Landing page live
2. ⬜ Set up domain (contractor.dev or similar)
3. ⬜ Connect demo form to real backend (Typeform / Airtable / email)
4. ⬜ Join developer communities and start contributing
5. ⬜ Write first 3 LinkedIn posts (problem-focused, no selling)
6. ✅ CLI MVP built (oasdiff engine + legacy fallback)
7. ⬜ Build auth + API key backend (FastAPI)
8. ⬜ 3 beta customers using CLI in CI/CD
9. ⬜ Launch Free plan on GitHub (open source)
10. ⬜ Product Hunt launch
