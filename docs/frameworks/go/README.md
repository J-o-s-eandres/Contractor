# Go — OpenAPI Export Guides

All three frameworks (Gin, Echo, Fiber) use **swaggo/swag** with the same annotation syntax. Only the middleware import changes.

## Shared Setup

```bash
go install github.com/swaggo/swag/cmd/swag@latest
```

Annotate your handler comments:

```go
// @Summary      Get user by ID
// @Description  Returns a single user
// @Tags         users
// @Produce      json
// @Param        id   path      int  true  "User ID"
// @Success      200  {object}  User
// @Router       /users/{id} [get]
func GetUser(c *gin.Context) { ... }
```

Generate the spec:

```bash
swag init --output ./docs
```

This creates `docs/swagger.json` and `docs/swagger.yaml`.

---

## Gin

```bash
go get -u github.com/swaggo/gin-swagger
go get -u github.com/swaggo/files
```

```go
import (
    swaggerFiles "github.com/swaggo/files"
    ginSwagger "github.com/swaggo/gin-swagger"
    _ "your-module/docs"  // swaggo output
)

r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
```

**CI/CD:**
```yaml
- run: swag init --output ./docs
- run: contractor diff --base docs/swagger.yaml --candidate openapi-prod.yaml
```

---

## Echo

```bash
go get -u github.com/swaggo/echo-swagger
```

```go
import (
    "github.com/swaggo/echo-swagger"
    _ "your-module/docs"
)

e.GET("/swagger/*", echoSwagger.WrapHandler)
```

**CI/CD:** Same as Gin (`swag init` then `contractor diff`).

---

## Fiber

> `gofiber/swagger` is archived. Use `gofiber/contrib/swaggo` instead.

```bash
go get -u github.com/gofiber/contrib/swaggo
```

```go
import (
    "github.com/gofiber/contrib/swaggo"
    _ "your-module/docs"
)

app.Get("/swagger/*", swaggo.New())
```

**CI/CD:** Same as Gin (`swag init` then `contractor diff`).
