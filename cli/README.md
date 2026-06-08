# contractor-cli

CLI tool to detect breaking changes in OpenAPI specs before they hit production.

## Install

```bash
pip install contractor-cli
```

Requires Python 3.11+ and [oasdiff](https://github.com/oasdiff/oasdiff) (`brew install oasdiff`).

## Usage

```bash
contractor diff --base main.yaml --candidate feature.yaml

# Output formats: console (default), json, markdown
contractor diff --base main.yaml --candidate feature.yaml --format json

# Legacy engine (no oasdiff needed):
contractor diff --base main.yaml --candidate feature.yaml --engine legacy
```

Exit codes: `0` = safe, `1` = breaking changes, `2` = error.

## Architecture

```
                    ┌─────────────────────────────┐
                    │        contractor diff       │
                    │           cli.py             │
                    └──────────┬──────────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼               ▼
        ┌────────────┐ ┌───────────┐ ┌──────────────┐
        │  oasdiff   │ │  parser   │ │   legacy     │
        │ (default)  │ │  YAML/   │ │   engine     │
        │ subprocess │ │  JSON    │ │  (fallback)  │
        └─────┬──────┘ └───────────┘ └──────┬───────┘
              │                              │
              ▼                              ▼
        ┌────────────┐              ┌────────────────┐
        │  adapter   │              │  4 detectors   │
        │ JSON →     │              │ endpoints      │
        │ Breaking   │              │ parameters     │
        │ Change     │              │ types          │
        └─────┬──────┘              │ required       │
              │                     └──────┬─────────┘
              └──────────────┬────────────┘
                             ▼
                    ┌────────────────┐
                    │  BreakingChange │
                    │    (models)     │
                    └───────┬────────┘
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
          ┌─────────┐ ┌─────────┐ ┌─────────┐
          │ console │ │  json   │ │ markdown│
          │  Rich   │ │  fmt    │ │ report  │
          └─────────┘ └─────────┘ └─────────┘
```

### Detection engines

**oasdiff** (default): Delegates all detection to oasdiff via subprocess (`oasdiff breaking --format json`). Covers 450+ breaking change rules. The JSON output is mapped to internal `BreakingChange` models via `oasdiff_adapter.py`.

**Legacy** (`--engine legacy`): Built-in fallback with 4 detection rules:
- `endpoints.py` — endpoint removed
- `parameters.py` — required param added
- `types.py` — type/format changed
- `required.py` — required field added in request body

### Output formatters

- `console.py` — colored table via Rich
- `json_fmt.py` — structured JSON
- `markdown.py` — markdown table for PR comments

## Development

```bash
# Setup
git clone https://github.com/J-o-s-eandres/Contractor
cd contractor/cli
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Build binary (Windows)
build-exe.bat
```

### Project structure

```
cli/
├── contractor/              # Main package (10 modules)
│   ├── cli.py              # CLI entry point (Click)
│   ├── detect.py           # oasdiff subprocess wrapper
│   ├── models.py           # BreakingChange dataclass
│   ├── parser.py           # YAML/JSON spec loader
│   ├── oasdiff_adapter.py  # JSON → BreakingChange mapper
│   ├── detectors/          # Legacy engine (4 rules)
│   └── formatters/         # console, json, markdown
├── tests/                   # 236 tests
├── templates/               # CI/CD templates
└── examples/                # Example specs
```

## CI/CD

See [`templates/github-action.yml`](templates/github-action.yml) for GitHub Actions setup.

## License

MIT
