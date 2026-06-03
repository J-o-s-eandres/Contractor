# 04 — Campo Requerido Agregado

El campo `tax_id` se agregó al array `required[]` del body de `POST /invoices`.

## Comando

```bash
cd cli/
python -m contractor diff \
  --base ../examples/04-required-field-added/base.yaml \
  --candidate ../examples/04-required-field-added/candidate.yaml
```

## Output esperado

```
!! 1 breaking change detected

+-----------------------------------------------------------------------------+
| Type                | Location      | Description                           |
|---------------------+---------------+---------------------------------------|
| required field added | body.tax_id   | Field 'tax_id' is now required        |
|                     |               | in body of POST /invoices             |
+-----------------------------------------------------------------------------+

Exit code: 1
```

## Por qué es breaking

Los clientes que envían facturas sin `tax_id` recibirán errores de validación. Todos los consumidores deben actualizar sus payloads para incluir este campo antes del deploy.
