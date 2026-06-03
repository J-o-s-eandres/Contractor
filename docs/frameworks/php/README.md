# PHP — OpenAPI Export Guides

## Laravel (with Scramble)

```bash
composer require dedoc/scramble
```

Scramble infers OpenAPI from Laravel route and FormRequest definitions — no annotations needed.

**Export:**
```bash
php artisan scramble:export openapi.json
```

**CI/CD:**
```yaml
- run: php artisan scramble:export openapi.json
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

---

## Symfony (with NelmioApiDocBundle)

```bash
composer require nelmio/api-doc-bundle
```

```yaml
# config/packages/nelmio_api_doc.yaml
nelmio_api_doc:
    documentation:
        info: { title: "My API", version: "1.0.0" }
```

Annotate controllers with `#[OA\Get]`, `#[OA\Post]`, etc.

**Export:**
```bash
php bin/console nelmio:apidoc:dump --format=yaml > openapi.yaml
```

**CI/CD:**
```yaml
- run: php bin/console nelmio:apidoc:dump --format=yaml > openapi.yaml
- run: contractor diff --base openapi-prod.yaml --candidate openapi.yaml
```
