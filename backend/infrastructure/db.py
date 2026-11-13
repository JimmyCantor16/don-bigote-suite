"""Infraestructura: base de datos y modelos ORM."""
from __future__ import annotations

import os

from sqlalchemy import (
    Boolean, Column, Float, ForeignKey, Integer, String, Text, create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

# La conexión se lee del ENTORNO, nunca fija en el código: así el mismo código
# corre con SQLite en tu portátil y con el MySQL o el PostgreSQL de tu servidor
# sin tocar una línea. Si no hay nada configurado, usa un archivo SQLite local.
_URL = os.environ.get("DATABASE_URL") or os.environ.get("DB_URL") or "sqlite:///./app.db"

# El prefijo se normaliza al driver que ESTE proyecto declara en requirements.
# Sin esto, SQLAlchemy elige el driver por defecto de cada motor —psycopg2 para
# `postgresql://` y MySQLdb para `mysql://`— y ninguno de los dos está
# instalado: la aplicación muere al arrancar con `ModuleNotFoundError`.
# Los prefijos ya explícitos se dejan intactos.
for _viejo, _nuevo in (
    ("postgresql+", None),
    ("mysql+", None),
    ("postgresql://", "postgresql+psycopg://"),
    ("postgres://", "postgresql+psycopg://"),
    ("mysql://", "mysql+pymysql://"),
):
    if _URL.startswith(_viejo):
        if _nuevo:
            _URL = _nuevo + _URL[len(_viejo):]
        break

# `check_same_thread` es exclusivo de SQLite: pasárselo a otro motor lo revienta.
_opciones = {"connect_args": {"check_same_thread": False}} if _URL.startswith("sqlite") else {"pool_pre_ping": True}

engine = create_engine(_URL, **_opciones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    es_admin = Column(Boolean, nullable=False, default=False)


class CitaModel(Base):
    __tablename__ = "citas"
    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(255), nullable=False)
    sede = Column(String(255), nullable=False)
    barbero = Column(String(255), nullable=False)
    servicio = Column(String(255), nullable=False)
    fecha = Column(String(32), nullable=False)
    hora = Column(String(120), nullable=False)
    estado = Column(String(120), nullable=False)
    monto = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)


class CatSedeModel(Base):
    __tablename__ = "cat_sedes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(255), nullable=False)
    telefono = Column(String(255), nullable=False)

class CatClienteModel(Base):
    __tablename__ = "cat_clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    telefono = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False)
    puntos = Column(Integer, nullable=False)

class CatBarberoModel(Base):
    __tablename__ = "cat_barberos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    sede = Column(String(255), nullable=False)
    comision = Column(Float, nullable=False)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


#: Cuenta de demostración. Existe para que quien reciba el enlace pueda MIRAR
#: el sistema en un clic, con datos dentro, sin registrarse. Sin esto, un
#: contacto abre una pantalla de login y un listado vacío: parece roto.
USUARIO_DEMO = "demo"
CLAVE_DEMO = "demo1234"

#: La cuenta del DUEÑO del negocio. Fija y documentada en el MANUAL: quien
#: recibe el sistema entra con ella, gestiona sus catálogos y ve todo. Cambiar
#: su contraseña es lo primero que el manual le pide hacer.
ADMIN_USUARIO = "admin"
ADMIN_CLAVE = "admin1234"

_EJEMPLOS = [{'cliente': 'Carlos Pineda', 'sede': 'Don Bigote Chapinero', 'barbero': 'Andrés Mejía', 'servicio': 'Corte + barba', 'fecha': '2026-11-13', 'hora': '09:00', 'estado': 'atendida', 'monto': 45000.0}, {'cliente': 'Felipe Arango', 'sede': 'Don Bigote Usaquén', 'barbero': 'Camilo Ruiz', 'servicio': 'Corte clásico', 'fecha': '2026-11-13', 'hora': '10:00', 'estado': 'confirmada', 'monto': 0.0}, {'cliente': 'Mauricio Gaviria', 'sede': 'Don Bigote Laureles', 'barbero': 'Sebastián Londoño', 'servicio': 'Afeitado clásico', 'fecha': '2026-11-13', 'hora': '11:00', 'estado': 'atendida', 'monto': 30000.0}, {'cliente': 'Daniel Escobar', 'sede': 'Don Bigote Chapinero', 'barbero': 'Julián Prada', 'servicio': 'Barba y toalla caliente', 'fecha': '2026-11-13', 'hora': '15:00', 'estado': 'pendiente', 'monto': 0.0}, {'cliente': 'Santiago Vélez', 'sede': 'Don Bigote Usaquén', 'barbero': 'Camilo Ruiz', 'servicio': 'Corte + barba', 'fecha': '2026-11-13', 'hora': '17:00', 'estado': 'pendiente', 'monto': 0.0}, {'cliente': 'Ricardo Salazar', 'sede': 'Don Bigote Chapinero', 'barbero': 'Andrés Mejía', 'servicio': 'Corte clásico', 'fecha': '2026-11-12', 'hora': '16:00', 'estado': 'atendida', 'monto': 28000.0}, {'cliente': 'Hernán Cardona', 'sede': 'Don Bigote Laureles', 'barbero': 'Sebastián Londoño', 'servicio': 'Arreglo de cejas', 'fecha': '2026-11-11', 'hora': '12:00', 'estado': 'cancelada', 'monto': 0.0}, {'cliente': 'Tomás Quintero', 'sede': 'Don Bigote Chapinero', 'barbero': 'Julián Prada', 'servicio': 'Corte clásico', 'fecha': '2026-11-07', 'hora': '14:00', 'estado': 'atendida', 'monto': 28000.0}, {'cliente': 'Carlos Pineda', 'sede': 'Don Bigote Usaquén', 'barbero': 'Camilo Ruiz', 'servicio': 'Barba y toalla caliente', 'fecha': '2026-11-04', 'hora': '18:00', 'estado': 'atendida', 'monto': 22000.0}, {'cliente': 'Esteban Murillo', 'sede': 'Don Bigote Laureles', 'barbero': 'Sebastián Londoño', 'servicio': 'Corte + barba', 'fecha': '2026-10-30', 'hora': '10:00', 'estado': 'atendida', 'monto': 45000.0}, {'cliente': 'Felipe Arango', 'sede': 'Don Bigote Usaquén', 'barbero': 'Camilo Ruiz', 'servicio': 'Corte clásico', 'fecha': '2026-10-24', 'hora': '11:00', 'estado': 'atendida', 'monto': 28000.0}]


def sembrar_demostracion(hasher) -> bool:
    """Deja el sistema LISTO PARA USAR en el primer arranque. True si sembró algo.

    Tres siembras independientes, cada una de un solo disparo:
      1. La cuenta del administrador (siempre, haya o no ejemplos).
      2. Los catálogos con sus filas iniciales (si sus tablas están vacías):
         sin barberos no se puede pedir cita, así que un catálogo vacío
         dejaría la aplicación inservible nada más nacer.
      3. La cuenta de demostración con sus registros (si hay ejemplos).
    """
    sembrado = False
    sesion = SessionLocal()
    try:
        admin = sesion.query(UserModel).filter(UserModel.username == ADMIN_USUARIO).first()
        if admin is None:
            sesion.add(UserModel(
                username=ADMIN_USUARIO, hashed_password=hasher.hash(ADMIN_CLAVE), es_admin=True,
            ))
            sesion.commit()
            sembrado = True

        for modelo, filas in _MODELOS_SEMILLA:
            if filas and sesion.query(modelo).first() is None:
                for fila in filas:
                    sesion.add(modelo(**fila))
                sesion.commit()
                sembrado = True

        if _EJEMPLOS:
            demo = sesion.query(UserModel).filter(UserModel.username == USUARIO_DEMO).first()
            if demo is None:
                demo = UserModel(username=USUARIO_DEMO, hashed_password=hasher.hash(CLAVE_DEMO))
                sesion.add(demo)
                sesion.flush()  # necesitamos su id para que los registros sean suyos
                for fila in _EJEMPLOS:
                    sesion.add(CitaModel(owner_id=demo.id, **fila))
                sesion.commit()
                sembrado = True
        return sembrado
    except Exception:  # noqa: BLE001 - sin datos de ejemplo la app sigue sirviendo
        sesion.rollback()
        return sembrado
    finally:
        sesion.close()


#: (modelo ORM, filas iniciales) de cada catálogo, para la siembra.
_MODELOS_SEMILLA = [
    (CatSedeModel, [{'nombre': 'Don Bigote Chapinero', 'direccion': 'Cra 13 #59-20, Bogotá', 'telefono': '601 345 7821'}, {'nombre': 'Don Bigote Usaquén', 'direccion': 'Cl 119 #6-30, Bogotá', 'telefono': '601 612 4403'}, {'nombre': 'Don Bigote Laureles', 'direccion': 'Cir 4 #70-15, Medellín', 'telefono': '604 411 9086'}]),
    (CatClienteModel, [{'nombre': 'Carlos Pineda', 'telefono': '310 455 2190', 'correo': 'carlos.pineda@gmail.com', 'puntos': 67}, {'nombre': 'Felipe Arango', 'telefono': '315 802 3347', 'correo': 'farango@hotmail.com', 'puntos': 56}, {'nombre': 'Mauricio Gaviria', 'telefono': '300 219 7765', 'correo': 'mauro.gaviria@gmail.com', 'puntos': 30}, {'nombre': 'Daniel Escobar', 'telefono': '321 640 1182', 'correo': 'daniel.escobar@outlook.com', 'puntos': 44}, {'nombre': 'Santiago Vélez', 'telefono': '317 993 0451', 'correo': 'santi.velez@gmail.com', 'puntos': 12}, {'nombre': 'Ricardo Salazar', 'telefono': '312 507 8826', 'correo': 'rsalazar@yahoo.com', 'puntos': 28}, {'nombre': 'Hernán Cardona', 'telefono': '304 118 6620', 'correo': 'hernan.cardona@gmail.com', 'puntos': 10}, {'nombre': 'Tomás Quintero', 'telefono': '318 276 4409', 'correo': 'tquintero@gmail.com', 'puntos': 28}, {'nombre': 'Esteban Murillo', 'telefono': '301 884 2953', 'correo': 'esteban.murillo@outlook.com', 'puntos': 45}]),
    (CatBarberoModel, [{'nombre': 'Andrés Mejía', 'sede': 'Don Bigote Chapinero', 'comision': 40.0}, {'nombre': 'Camilo Ruiz', 'sede': 'Don Bigote Usaquén', 'comision': 45.0}, {'nombre': 'Sebastián Londoño', 'sede': 'Don Bigote Laureles', 'comision': 40.0}, {'nombre': 'Julián Prada', 'sede': 'Don Bigote Chapinero', 'comision': 35.0}]),
]
