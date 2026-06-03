# Extra — OpenAPI Export Guides

## Kotlin Ktor

```kotlin
// build.gradle.kts
implementation("io.ktor:ktor-server-openapi:$ktor_version")
```

```kotlin
// Application.kt
fun Application.module() {
    install(OpenAPI) {
        swaggerUI("/swagger-ui")
        specPath = "/openapi.json"
    }
}
```

**Export:**
```bash
# Start app, then curl
curl -s http://localhost:8080/openapi.json > openapi.json
```

**CI/CD:**
```yaml
- run: |
    ./gradlew run &
    sleep 10
    curl -s http://localhost:8080/openapi.json > openapi.json
    kill %1
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

---

## Elixir Phoenix (with phoenix_openapi)

```elixir
# mix.exs
defp deps do
  [
    {:phoenix_openapi, "~> 0.2"}
  ]
end
```

```elixir
# lib/my_app_web/router.ex
use Phoenix.OpenAPI

open_api do
  info do
    title "My API"
    version "1.0.0"
  end
end
```

**Export:**
```elixir
# scripts/export_openapi.exs
Mix.Task.run("openapi.generate")
```

Or at runtime via a Plug endpoint.

**CI/CD:**
```yaml
- run: mix run scripts/export_openapi.exs
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

---

## Scala Play (with play-swagger)

```scala
// build.sbt
libraryDependencies += "com.codacy" %% "play-swagger" % "0.10.0"
```

Use `@ApiModel` annotations on case classes, route comments for endpoints.

**Export:**
```bash
sbt "swagger"
# Output: target/swagger/openapi.json
```

**CI/CD:**
```yaml
- run: sbt swagger
- run: contractor diff --base target/swagger/openapi.json --candidate openapi-prod.json
```
