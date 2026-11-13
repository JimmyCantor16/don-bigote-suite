# Don Bigote Suite

Aplicación para gestionar citas, con cuenta propia.
Backend **hexagonal** (dominio / aplicación / infraestructura) y frontend por
componentes que se dibuja a partir del dominio.

## Qué guarda cada cita

- **Cliente** (relacion)
- **Sede** (relacion)
- **Barbero** (relacion)
- **Servicio** (texto)
- **Fecha** (fecha)
- **Hora** (opcion)
- **Estado** (opcion)
- **Monto cobrado (solo si fue atendida)** (decimal)

## Para enseñárselo a alguien

La aplicación arranca con **11 citas de ejemplo** ya dentro, para que quien abra el enlace vea un sistema en uso en vez de una pantalla en blanco.

En la pantalla de entrada hay un botón **«Ver una demostración»**: entra sin registrarse y puede mirar todo. Los datos son inventados.

| | |
|---|---|
| Usuario | `demo` |
| Contraseña | `demo1234` |

Quien quiera guardar lo suyo crea su cuenta: cada usuario ve solo sus citas, nunca los de otro.

## Correr

```
pip install -r backend/requirements.txt
uvicorn backend.main:app
```

Abre http://localhost:8000
