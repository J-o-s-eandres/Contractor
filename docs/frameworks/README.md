# Supported Frameworks

> How to automatically export OpenAPI specs from any framework for use with `contractor diff`.

## Quick Reference

| Language | Framework | Library / Tool | Export Method | Spec Version |
|----------|-----------|---------------|---------------|--------------|
| **Python** | FastAPI | Built-in (`app.openapi()`) | Runtime JSON dump | 3.1 |
| | Flask | APISpec / flask-smorest | Runtime YAML/JSON | 3.0 |
| | Django | drf-spectacular | Management command | 3.0 |
| | Falcon | falcon-apispec | Runtime YAML | 3.0 |
| **JavaScript** | Express | swagger-jsdoc + swagger-ui-express | Runtime JSON | 3.0 |
| | NestJS | `@nestjs/swagger` | CLI plugin / runtime | 3.0 |
| | Fastify | `@fastify/swagger` | Runtime JSON | 3.0 |
| | Next.js | next-swagger-doc | Build-time JSON | 3.0 |
| | Koa | koa2-swagger-ui / swagger-jsdoc | Runtime JSON | 3.0 |
| **Java** | Spring Boot | springdoc-openapi | Runtime endpoint (`/v3/api-docs`) | 3.0 |
| | Micronaut | micronaut-openapi | Compile-time (`mn:openapi`) | 3.0 |
| | Quarkus | quarkus-smallrye-openapi | Compile-time (`mvn verify`) | 3.0 |
| **Go** | Gin | swaggo/swag | CLI (`swag init`) + runtime | 3.0 |
| | Echo | swaggo/swag | CLI (`swag init`) + runtime | 3.0 |
| | Fiber | swaggo/swag (via `gofiber/contrib`) | CLI (`swag init`) + runtime | 3.0 |
| **PHP** | Laravel | Scramble | Runtime (no annotations) | 3.0 |
| | Symfony | NelmioApiDocBundle | Command (`nelmio:apidoc:dump`) | 3.0 |
| **Ruby** | Rails | rswag | RSpec-driven specs → OpenAPI | 3.0 |
| | Sinatra | sinatra-swagger / swagger-blocks | Runtime JSON | 3.0 |
| **Rust** | Actix-Web | utoipa + utoipa-swagger | Compile-time macros | 3.0 |
| | Axum | utoipa + utoipa-swagger-ui | Compile-time macros | 3.0 |
| **C#** | ASP.NET Core | Microsoft.AspNetCore.OpenApi | Runtime endpoint (`/openapi/v1.json`) | 3.1 |
| **Kotlin** | Ktor | Ktor OpenAPI plugin | Compile-time / runtime | 3.0 |
| **Elixir** | Phoenix | Phoenix.OpenAPI | Runtime JSON via Plug | 3.0 |
| **Scala** | Play | play-swagger (Codacy) | sbt task → JSON | 3.0 |

## CI/CD Snippet (Generic)

```yaml
# Extract OpenAPI spec from your service (adjust per framework)
# then compare against the production spec:
contractor diff --base openapi-prod.yaml --candidate openapi-current.yaml
```

See each framework's guide for the exact export command.

## Per-Language Guides

- [Python](python/README.md) — FastAPI, Flask, Django, Falcon
- [JavaScript](javascript/README.md) — Express, NestJS, Fastify, Next.js, Koa
- [Java](java/README.md) — Spring Boot, Micronaut, Quarkus
- [Go](go/README.md) — Gin, Echo, Fiber
- [PHP](php/README.md) — Laravel, Symfony
- [Ruby](ruby/README.md) — Rails, Sinatra
- [Rust](rust/README.md) — Actix-Web, Axum
- [C#](csharp/README.md) — ASP.NET Core
- [Extra](extra/README.md) — Kotlin Ktor, Elixir Phoenix, Scala Play
