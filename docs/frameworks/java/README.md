# Java — OpenAPI Export Guides

## Spring Boot (with springdoc-openapi)

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.6.0</version>
</dependency>
```

Once added, the spec is served at `/v3/api-docs` at runtime.

**Export:**
```bash
# Start app, then curl the endpoint
mvn spring-boot:run &
sleep 10
curl -s http://localhost:8080/v3/api-docs > openapi.json
kill %1
```

**CI/CD:**
```yaml
- run: |
    mvn spring-boot:run -Dspring-boot.run.arguments="--server.port=8080" &
    sleep 15
    curl -s http://localhost:8080/v3/api-docs > openapi.json
    kill %1
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

> **Note:** Spring Boot requires the app to be running. For CI, use a ephemeral port and graceful shutdown.

---

## Micronaut (with micronaut-openapi)

```xml
<!-- pom.xml -->
<dependency>
    <groupId>io.micronaut.openapi</groupId>
    <artifactId>micronaut-openapi</artifactId>
    <scope>compile</scope>
</dependency>
```

Annotate your controller:

```java
@OpenAPIDefinition(info = @Info(title = "My API", version = "1.0.0"))
@Controller("/api")
public class MyController { ... }
```

**Export (compile-time, no server needed):**
```bash
./gradlew generateOpenApiDocs
# or
./mvnw generateOpenApiDocs
```

Output is at `build/classes/java/main/META-INF/swagger/my-api.yml`.

**CI/CD:**
```yaml
- run: ./mvnw generateOpenApiDocs
- run: cp build/classes/java/main/META-INF/swagger/my-api.yml openapi.yml
- run: contractor diff --base openapi-prod.yml --candidate openapi.yml
```

---

## Quarkus (with quarkus-smallrye-openapi)

```xml
<!-- pom.xml -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-openapi</artifactId>
</dependency>
```

**Export (compile-time, no server needed):**
```bash
./mvnw verify
# Spec is generated at target/openapi.yaml (or target/openapi.json)
```

**CI/CD:**
```yaml
- run: ./mvnw verify
- run: contractor diff --base openapi-prod.yaml --candidate target/openapi.yaml
```
