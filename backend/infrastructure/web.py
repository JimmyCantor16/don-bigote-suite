"""Entrypoint HTTP: traduce peticiones en llamadas a los casos de uso."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.application.services import (
    AuthError, AuthService, CatalogoService, PermisoError, ValidacionError, CitaService,
)
from backend.domain.entities import User
from backend.infrastructure.db import SessionLocal
from backend.infrastructure.repositories import (
    SqlCatalogoRepository, SqlUserRepository, SqlCitaRepository,
)
from backend.infrastructure.security import BcryptHasher, JwtTokenService

router = APIRouter(prefix="/api")
_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/login")


class Credentials(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    es_admin: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegistroIn(BaseModel):
    cliente: str
    sede: str
    barbero: str
    servicio: str
    fecha: str
    hora: str
    estado: str
    monto: float


class RegistroOut(BaseModel):
    id: int
    cliente: str | None = None
    sede: str | None = None
    barbero: str | None = None
    servicio: str | None = None
    fecha: str | None = None
    hora: str | None = None
    estado: str | None = None
    monto: float | None = None
    #: Solo en la vista del administrador: de quién es cada registro.
    dueno: str | None = None


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_auth(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(SqlUserRepository(session), BcryptHasher(), JwtTokenService())


def get_servicio(session: Session = Depends(get_session)) -> CitaService:
    return CitaService(SqlCitaRepository(session), SqlCatalogoRepository(session))


def get_catalogos(session: Session = Depends(get_session)) -> CatalogoService:
    return CatalogoService(SqlCatalogoRepository(session))


def current_user(token: str = Depends(_oauth2), auth: AuthService = Depends(get_auth)) -> User:
    user = auth.user_from_token(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")
    return user


@router.post("/register", response_model=UserOut)
def register(body: Credentials, auth: AuthService = Depends(get_auth)):
    try:
        user = auth.register(body.username, body.password)
    except (ValidacionError, AuthError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return UserOut(id=user.id, username=user.username)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), auth: AuthService = Depends(get_auth)):
    try:
        return Token(access_token=auth.login(form.username, form.password))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.get("/me", response_model=UserOut)
def quien_soy(user: User = Depends(current_user)):
    """El frontend decide con esto si muestra el panel de administración."""
    return UserOut(id=user.id or 0, username=user.username, es_admin=user.es_admin)


@router.get("/catalogos")
def ver_catalogos(user: User = Depends(current_user), svc: CatalogoService = Depends(get_catalogos)):
    """Todos los catálogos con sus ítems: alimenta los desplegables del formulario."""
    return svc.listar_todos()


@router.post("/catalogos/{slug}")
def crear_en_catalogo(slug: str, body: dict, user: User = Depends(current_user),
                      svc: CatalogoService = Depends(get_catalogos)):
    try:
        return svc.crear(user, slug, body)
    except PermisoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValidacionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/catalogos/{slug}/{item_id}")
def borrar_de_catalogo(slug: str, item_id: int, user: User = Depends(current_user),
                       svc: CatalogoService = Depends(get_catalogos)):
    try:
        if not svc.borrar(user, slug, item_id):
            raise HTTPException(status_code=404, detail="No encontrado")
    except PermisoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValidacionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True}


@router.get("/registros", response_model=list[RegistroOut])
def listar(user: User = Depends(current_user), svc: CitaService = Depends(get_servicio)):
    return [
        RegistroOut(id=r.id, cliente=r.cliente, sede=r.sede, barbero=r.barbero, servicio=r.servicio, fecha=r.fecha, hora=r.hora, estado=r.estado, monto=r.monto, dueno=dueno)
        for r, dueno in svc.list_para(user)
    ]


@router.post("/registros", response_model=RegistroOut)
def crear(body: RegistroIn, user: User = Depends(current_user),
          svc: CitaService = Depends(get_servicio)):
    try:
        r = svc.create(user.id, body.model_dump())
    except ValidacionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RegistroOut(id=r.id, cliente=r.cliente, sede=r.sede, barbero=r.barbero, servicio=r.servicio, fecha=r.fecha, hora=r.hora, estado=r.estado, monto=r.monto)


@router.put("/registros/{registro_id}", response_model=RegistroOut)
def actualizar(registro_id: int, body: RegistroIn, user: User = Depends(current_user),
               svc: CitaService = Depends(get_servicio)):
    try:
        # El admin corrige el de cualquiera; los demás, solo el suyo.
        r = svc.update_como(user, registro_id, body.model_dump())
    except ValidacionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if r is None:
        raise HTTPException(status_code=404, detail="No encontrado")
    return RegistroOut(id=r.id, cliente=r.cliente, sede=r.sede, barbero=r.barbero, servicio=r.servicio, fecha=r.fecha, hora=r.hora, estado=r.estado, monto=r.monto)


@router.delete("/registros/{registro_id}")
def borrar(registro_id: int, user: User = Depends(current_user),
           svc: CitaService = Depends(get_servicio)):
    # El administrador puede cancelar el registro de cualquiera (la dueña
    # cancela citas); los demás solo el suyo.
    if not svc.delete_como(user, registro_id):
        raise HTTPException(status_code=404, detail="No encontrado")
    return {"ok": True}


@router.get("/resumen")
def resumen(user: User = Depends(current_user), svc: CitaService = Depends(get_servicio)):
    """Los cálculos declarados en el dominio, sobre lo que este usuario ve."""
    return svc.resumen_para(user)
