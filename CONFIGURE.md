# Configurar Don Bigote Suite

## 1. Las variables

Copia `.env.example` a `.env`:

```
cp .env.example .env
```

- `DATABASE_URL`: dónde está la base de datos.
- `SECRET_KEY`: **cámbiala**. Con la de ejemplo, cualquiera que la
  conozca podría entrar como cualquier usuario.

## 2. La base de datos (SQLite)

No hay que instalar ninguna base de datos: SQLite es un archivo
(`app.db`) que se crea solo la primera vez que arrancas.

## 3. Arrancar

```
pip install -r backend/requirements.txt
uvicorn backend.main:app
```

Abre http://localhost:8000
