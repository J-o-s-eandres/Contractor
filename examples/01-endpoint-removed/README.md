# 01 — Endpoint Eliminado

El endpoint `DELETE /users/{id}` existe en la especificación base pero fue eliminado en la candidata.

## Comando

```bash
cd cli/
python -m contractor diff \
  --base ../examples/01-endpoint-removed/base.yaml \
  --candidate ../examples/01-endpoint-removed/candidate.yaml
```

## Output esperado

```
!! 1 breaking change detected

+-------------------------------------------------------------------+
| Type              | Location           | Description               |
|-------------------+--------------------+---------------------------|
| endpoint removed  | DELETE /users/{id} | Endpoint DELETE           |
|                   |                    | /users/{id} was removed   |
+-------------------------------------------------------------------+

Exit code: 1
```

## Por qué es breaking

Cualquier cliente que consume `DELETE /users/{id}` fallará al hacer llamadas a esa URL. El equipo frontend (o el microservicio dependiente) debe ser notificado antes de mergear.
