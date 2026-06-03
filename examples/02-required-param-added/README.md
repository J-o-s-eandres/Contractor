# 02 — Parámetro Requerido Agregado

El parámetro `?filter` en `GET /products` cambió de `required: false` a `required: true`.

## Comando

```bash
cd cli/
python -m contractor diff \
  --base ../examples/02-required-param-added/base.yaml \
  --candidate ../examples/02-required-param-added/candidate.yaml
```

## Output esperado

```
!! 1 breaking change detected

+-------------------------------------------------------------------------+
| Type                 | Location        | Description                     |
|----------------------+-----------------+---------------------------------|
| required param added | parameter:filter | Parameter 'filter' became      |
|                      |                 | required in GET /products       |
+-------------------------------------------------------------------------+

Exit code: 1
```

## Por qué es breaking

Los clientes que llaman a `GET /products` sin el parámetro `filter` empezarán a recibir errores 400. Todos los consumidores de este endpoint deben actualizar sus llamadas antes del deploy.
