# JavaScript / TypeScript — OpenAPI Export Guides

## Express (with swagger-jsdoc)

```bash
npm install swagger-jsdoc
```

```javascript
// scripts/export-openapi.js
const swaggerJsdoc = require("swagger-jsdoc");
const fs = require("fs");

const options = {
  definition: { openapi: "3.0.0", info: { title: "My API", version: "1.0.0" } },
  apis: ["./src/routes/*.js"],
};

const spec = swaggerJsdoc(options);
fs.writeFileSync("openapi.json", JSON.stringify(spec, null, 2));
```

**CI/CD:**
```yaml
- run: node scripts/export-openapi.js
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

---

## NestJS

```bash
npm install @nestjs/swagger
```

```typescript
// main.ts (already bootstrapped)
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";

const config = new DocumentBuilder().setTitle("My API").setVersion("1.0").build();
const document = SwaggerModule.createDocument(app, config);

// Export on startup
import * as fs from "fs";
fs.writeFileSync("./openapi.json", JSON.stringify(document, null, 2));
```

**CI/CD:**
```yaml
- run: npm run start & sleep 5 && kill %1  # produces openapi.json
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

---

## Fastify

```bash
npm install @fastify/swagger
```

```javascript
// app.js
const fastify = require("fastify")();
fastify.register(require("@fastify/swagger"), {
  openapi: { info: { title: "My API", version: "1.0.0" } },
});

// Export after all routes are registered
await fastify.ready();
const spec = fastify.swagger();
require("fs").writeFileSync("openapi.json", JSON.stringify(spec, null, 2));
```

**CI/CD:**
```yaml
- run: node app.js  # writes openapi.json on startup
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

---

## Next.js (with next-swagger-doc)

```bash
npm install next-swagger-doc
```

```javascript
// next-swagger-doc.json
{ "apiFolder": "src/pages/api", "definition": { "openapi": "3.0.0", "info": { "title": "My API", "version": "1.0.0" } } }
```

**Export:**
```bash
npx next-swagger-doc-cli --output openapi.json
```

**CI/CD:**
```yaml
- run: npx next-swagger-doc-cli --output openapi.json
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

---

## Koa (with swagger-jsdoc)

Same pattern as Express:

```bash
npm install swagger-jsdoc
```

```javascript
// scripts/export-openapi.js
const swaggerJsdoc = require("swagger-jsdoc");
const fs = require("fs");

const spec = swaggerJsdoc({
  definition: { openapi: "3.0.0", info: { title: "My API", version: "1.0.0" } },
  apis: ["./src/routes/*.js"],
});
fs.writeFileSync("openapi.json", JSON.stringify(spec, null, 2));
```

**CI/CD:** Same as Express.
