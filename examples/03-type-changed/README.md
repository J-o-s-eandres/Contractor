# 03 — Tipo de Campo Cambiado

El campo `amount` en el body de `POST /payments` cambió de `type: string` a `type: number`.

## Comando

```bash
cd cli/
python -m contractor diff \
  --base ../examples/03-type-changed/base.yaml \
  --candidate ../examples/03-type-changed/candidate.yaml
```

## Output esperado

```
!! 1 breaking change detected

+-------------------------------------------------------------------------+
| Type          | Location     | Description                               |
|---------------+--------------+-------------------------------------------|
| type changed  | body.amount  | Field 'body.amount' type changed:         |
|               |              | 'string' -> 'number'                      |
+-------------------------------------------------------------------------+

Exit code: 1
```

## Por qué es breaking

Los clientes que envían `amount` como string (ej: `"99.99"`) recibirán errores de validación si el servidor ahora espera un número (`99.99`). Tipos de lenguajes sin coerción automática (Python, Rust, Go) pueden fallar en tiempo de ejecución.
