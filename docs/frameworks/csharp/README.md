# C# — OpenAPI Export Guide

## ASP.NET Core

> Swashbuckle is deprecated in .NET 9+. Use `Microsoft.AspNetCore.OpenApi` (built-in).

```xml
<!-- .csproj -->
<PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="9.0.0" />
```

```csharp
// Program.cs
using Microsoft.AspNetCore.OpenApi;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddOpenApi();

var app = builder.Build();
app.MapOpenApi();  // serves spec at /openapi/v1.json

app.Run();
```

**Export:**
```bash
# Start app, then curl
dotnet run --urls http://localhost:5000 &
sleep 5
curl -s http://localhost:5000/openapi/v1.json > openapi.json
kill %1
```

**CI/CD:**
```yaml
- run: |
    dotnet run --urls http://localhost:5000 &
    sleep 10
    curl -s http://localhost:5000/openapi/v1.json > openapi.json
    kill %1
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```
