# Python — OpenAPI Export Guides

## FastAPI

FastAPI generates OpenAPI 3.1 automatically from type hints.

```python
# scripts/export_openapi.py
import json
from my_app.main import app

with open("openapi.yaml", "w") as f:
    json.dump(app.openapi(), f, indent=2)
```

**CI/CD:**
```yaml
- run: python scripts/export_openapi.py
- run: contractor diff --base openapi-prod.yaml --candidate openapi.yaml
```

---

## Flask (with flask-smorest)

```python
# app.py
from flask_smorest import Api
api = Api(app)  # registers OpenAPI view at /openapi.json
```

**Export:**
```bash
curl -s http://localhost:5000/openapi.json > openapi.json
```

**CI/CD:**
```yaml
- run: |
    gunicorn app:app &
    sleep 2
    curl -s http://localhost:5000/openapi.json > openapi.json
    kill %1
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```

---

## Django (with drf-spectacular)

```bash
pip install drf-spectacular
```

```python
# settings.py
INSTALLED_APPS += ["drf_spectacular"]
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
SPECTACULAR_SETTINGS = {"TITLE": "My API", "VERSION": "1.0.0"}
```

**Export:**
```bash
python manage.py spectacular --file openapi.yaml --format yaml
```

**CI/CD:**
```yaml
- run: python manage.py spectacular --file openapi.yaml --format yaml
- run: contractor diff --base openapi-prod.yaml --candidate openapi.yaml
```

---

## Falcon (with falcon-apispec)

```python
# export_openapi.py
import json
from falcon_apispec import FalconApiSpec
from my_app import api

spec = FalconApiSpec(api)
with open("openapi.json", "w") as f:
    json.dump(spec.to_dict(), f, indent=2)
```

**CI/CD:** Same pattern — run the export script then `contractor diff`.
