# Contractor CLI

Detect breaking changes in your API contracts before they hit production.

## Installation

### Binary (recommended — no Python needed)

Download from [GitHub Releases](https://github.com/your-org/contractor/releases).

### pip

```
pip install contractor
```

## Usage

```
contractor diff --base main/openapi.yaml --candidate feature/openapi.yaml
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--base` | Path to the baseline OpenAPI spec | required |
| `--candidate` | Path to the candidate OpenAPI spec | required |
| `--format` | Output format: `console`, `json`, `markdown` | `console` |
| `--output` | Write a Markdown report to this file | none |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | No breaking changes — safe to merge |
| `1` | Breaking changes detected — review required |
| `2` | Usage error (file not found, invalid flag) |

## What we detect

| Breaking change | Example |
|-----------------|---------|
| Endpoint removed | `DELETE /users/{id}` no longer exists |
| Required parameter added | `?filter=` changed from optional to required |
| Field type changed | `amount: string` -> `amount: number` |
| Required field added | `notes` added to `required[]` in request body |

## CI/CD Integration

### GitHub Actions

Copy `templates/github-action.yml` to `.github/workflows/contractor.yml`.

### GitLab CI

```yaml
api-contract-check:
  script:
    - ./contractor diff --base openapi/main.yaml --candidate openapi/feature.yaml --output report.md
  artifacts:
    when: on_failure
    paths: [report.md]
```

## License

MIT
