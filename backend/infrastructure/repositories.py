"""Adaptadores: implementan los puertos con SQLAlchemy."""
from __future__ import annotations

from sqlalchemy.orm import Session

from backend.domain.entities import Cita, User
from backend.domain.ports import CatalogoRepository, UserRepository, CitaRepository
from backend.infrastructure.db import UserModel, CitaModel, CatSedeModel, CatClienteModel, CatBarberoModel


def _a_user(row: UserModel) -> User:
    return User(id=row.id, username=row.username, es_admin=bool(row.es_admin))


def _a_entidad(row: CitaModel) -> Cita:
    return Cita(id=row.id, cliente=row.cliente, sede=row.sede, barbero=row.barbero, servicio=row.servicio, fecha=row.fecha, hora=row.hora, estado=row.estado, monto=row.monto, owner_id=row.owner_id)


class SqlUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def by_username(self, username: str) -> User | None:
        row = self._s.query(UserModel).filter(UserModel.username == username).first()
        return _a_user(row) if row else None

    def hashed_password(self, username: str) -> str | None:
        row = self._s.query(UserModel).filter(UserModel.username == username).first()
        return row.hashed_password if row else None

    def create(self, username: str, hashed_password: str) -> User:
        row = UserModel(username=username, hashed_password=hashed_password)
        self._s.add(row)
        self._s.commit()
        self._s.refresh(row)
        return _a_user(row)


class SqlCitaRepository(CitaRepository):
    def __init__(self, session: Session) -> None:
        self._s = session

    def list_for(self, owner_id: int) -> list[Cita]:
        filas = (
            self._s.query(CitaModel)
            .filter(CitaModel.owner_id == owner_id)
            .order_by(CitaModel.id.desc())
            .all()
        )
        return [_a_entidad(f) for f in filas]

    def list_all(self) -> list[tuple[Cita, str]]:
        """Todo con su dueño: la vista del administrador."""
        filas = (
            self._s.query(CitaModel, UserModel.username)
            .join(UserModel, UserModel.id == CitaModel.owner_id)
            .order_by(CitaModel.id.desc())
            .all()
        )
        return [(_a_entidad(f), username) for f, username in filas]

    def create(self, owner_id: int, datos: dict) -> Cita:
        row = CitaModel(owner_id=owner_id, cliente=datos.get('cliente'), sede=datos.get('sede'), barbero=datos.get('barbero'), servicio=datos.get('servicio'), fecha=datos.get('fecha'), hora=datos.get('hora'), estado=datos.get('estado'), monto=datos.get('monto'))
        self._s.add(row)
        self._s.commit()
        self._s.refresh(row)
        return _a_entidad(row)

    def get(self, registro_id: int, owner_id: int) -> Cita | None:
        row = self._buscar(registro_id, owner_id)
        return _a_entidad(row) if row else None

    def update(self, registro_id: int, owner_id: int, datos: dict) -> Cita | None:
        row = self._buscar(registro_id, owner_id)
        if row is None:
            return None
        if 'cliente' in datos:
            row.cliente = datos['cliente']
        if 'sede' in datos:
            row.sede = datos['sede']
        if 'barbero' in datos:
            row.barbero = datos['barbero']
        if 'servicio' in datos:
            row.servicio = datos['servicio']
        if 'fecha' in datos:
            row.fecha = datos['fecha']
        if 'hora' in datos:
            row.hora = datos['hora']
        if 'estado' in datos:
            row.estado = datos['estado']
        if 'monto' in datos:
            row.monto = datos['monto']
        self._s.commit()
        self._s.refresh(row)
        return _a_entidad(row)

    def delete(self, registro_id: int, owner_id: int) -> bool:
        row = self._buscar(registro_id, owner_id)
        if row is None:
            return False
        self._s.delete(row)
        self._s.commit()
        return True

    def update_any(self, registro_id: int, datos: dict) -> Cita | None:
        """Sin filtro de dueño. El servicio ya comprobó que quien pide es admin."""
        row = self._s.query(CitaModel).filter(CitaModel.id == registro_id).first()
        if row is None:
            return None
        if 'cliente' in datos:
            row.cliente = datos['cliente']
        if 'sede' in datos:
            row.sede = datos['sede']
        if 'barbero' in datos:
            row.barbero = datos['barbero']
        if 'servicio' in datos:
            row.servicio = datos['servicio']
        if 'fecha' in datos:
            row.fecha = datos['fecha']
        if 'hora' in datos:
            row.hora = datos['hora']
        if 'estado' in datos:
            row.estado = datos['estado']
        if 'monto' in datos:
            row.monto = datos['monto']
        self._s.commit()
        self._s.refresh(row)
        return _a_entidad(row)

    def delete_any(self, registro_id: int) -> bool:
        """Sin filtro de dueño. El servicio ya comprobó que quien pide es admin."""
        row = self._s.query(CitaModel).filter(CitaModel.id == registro_id).first()
        if row is None:
            return False
        self._s.delete(row)
        self._s.commit()
        return True

    def _buscar(self, registro_id: int, owner_id: int):
        return (
            self._s.query(CitaModel)
            .filter(CitaModel.id == registro_id, CitaModel.owner_id == owner_id)
            .first()
        )


class SqlCatalogoRepository(CatalogoRepository):
    """Un solo adaptador para todos los catálogos, guiado por estos mapas."""

    _MODELOS = {'sedes': CatSedeModel, 'clientes': CatClienteModel, 'barberos': CatBarberoModel}
    _COLUMNAS = {'sedes': ['nombre', 'direccion', 'telefono'], 'clientes': ['nombre', 'telefono', 'correo', 'puntos'], 'barberos': ['nombre', 'sede', 'comision']}
    #: La columna que hace de NOMBRE del ítem (la que ven los desplegables).
    _VISIBLE = {'sedes': 'nombre', 'clientes': 'nombre', 'barberos': 'nombre'}

    def __init__(self, session: Session) -> None:
        self._s = session

    def listar(self, slug: str) -> list[dict]:
        modelo = self._MODELOS.get(slug)
        if modelo is None:
            return []
        filas = self._s.query(modelo).order_by(modelo.id).all()
        columnas = self._COLUMNAS[slug]
        return [
            {"id": f.id, **{col: getattr(f, col) for col in columnas}}
            for f in filas
        ]

    def crear(self, slug: str, datos: dict) -> dict:
        modelo = self._MODELOS[slug]
        columnas = self._COLUMNAS[slug]
        row = modelo(**{col: datos.get(col) for col in columnas})
        self._s.add(row)
        self._s.commit()
        self._s.refresh(row)
        return {"id": row.id, **{col: getattr(row, col) for col in columnas}}

    def borrar(self, slug: str, item_id: int) -> bool:
        modelo = self._MODELOS.get(slug)
        if modelo is None:
            return False
        row = self._s.query(modelo).filter(modelo.id == item_id).first()
        if row is None:
            return False
        self._s.delete(row)
        self._s.commit()
        return True

    def existe_valor(self, slug: str, valor: str) -> bool:
        modelo = self._MODELOS.get(slug)
        if modelo is None:
            return False
        visible = getattr(modelo, self._VISIBLE[slug])
        return self._s.query(modelo).filter(visible == valor).first() is not None
