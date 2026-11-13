# Publicar Don Bigote Suite en internet

Pensado para alguien que no lo ha hecho nunca. Render tiene plan gratis
y es lo más corto.

## 1. Sube el código a GitHub

```
git init -b main
git add .
git commit -m "mi aplicación"
```

Crea un repositorio en github.com y sigue las dos líneas que te muestra
para enlazarlo y subirlo.

## 2. Crea el servicio

En https://dashboard.render.com elige **New → Web Service** y conecta tu
repositorio. Rellena:

| Campo | Valor |
|---|---|
| Build Command | `pip install -r backend/requirements.txt` |
| Start Command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |

## 3. La base de datos

No hace falta nada: SQLite viaja con la aplicación. Ten en cuenta que
en el plan gratis el disco se borra en cada despliegue; cuando quieras
que los datos duren, crea un PostgreSQL en Render y pon su dirección
en `DATABASE_URL` (el código ya lo admite sin cambiar nada).

## 4. La clave

Añade también `SECRET_KEY` con un valor largo y aleatorio.

## 5. Comprueba

Abre la URL que te da Render. Debe salir la pantalla de entrar.
