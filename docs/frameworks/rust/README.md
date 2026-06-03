# Rust — OpenAPI Export Guides

Both Actix-Web and Axum use **utoipa** with compile-time macro expansion.

## Shared Setup

```toml
# Cargo.toml
[dependencies]
utoipa = { version = "4", features = ["actix_extras"] }
utoipa-swagger-ui = { version = "7", features = ["actix-web"] }
```

Annotate your structs and handlers:

```rust
use utoipa::{OpenApi, ToSchema};

#[derive(ToSchema)]
#[schema(example = json!({"id": 1, "name": "Alice"}))]
struct User {
    id: i32,
    name: String,
}

#[utoipa::path(
    get,
    path = "/users/{id}",
    params(("id" = i32, Path, description = "User ID")),
    responses((status = 200, body = User))
)]
async fn get_user() -> impl Responder { ... }
```

Build the spec struct:

```rust
#[derive(OpenApi)]
#[openapi(paths(get_user), components(schemas(User)))]
struct ApiDoc;
```

## Actix-Web

```rust
use utoipa_swagger_ui::SwaggerUi;

HttpServer::new(move || {
    App::new()
        .service(SwaggerUi::new("/swagger-ui/{_:.*}").url("/api-doc/openapi.json", ApiDoc::openapi()))
})
```

**Export (build-time JSON):**
```rust
// build.rs or a binary target
fn main() {
    let spec = serde_json::to_string_pretty(&ApiDoc::openapi()).unwrap();
    std::fs::write("openapi.json", spec).unwrap();
}
```

**CI/CD:**
```yaml
- run: cargo run --bin export_openapi
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

## Axum

```toml
utoipa-swagger-ui = { version = "7", features = ["axum"] }
```

```rust
use utoipa_swagger_ui::SwaggerUi;

let app = Router::new()
    .merge(SwaggerUi::new("/swagger-ui").url("/api-doc/openapi.json", ApiDoc::openapi()));
```

**CI/CD:** Same as Actix-Web — write `ApiDoc::openapi()` to file, then `contractor diff`.
