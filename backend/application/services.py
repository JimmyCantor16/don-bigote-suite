"""Casos de uso: dependen SOLO de puertos."""
from __future__ import annotations

import re

from backend.domain.entities import Cita, User
from backend.domain.ports import (
    CatalogoRepository,
    PasswordHasher,
    TokenService,
    UserRepository,
    CitaRepository,
)


class AuthError(Exception):
    """Credenciales inválidas o usuario ya existente."""


class ValidacionError(Exception):
    """Los datos recibidos no cumplen las reglas del dominio."""


class PermisoError(Exception):
    """La operación exige ser administrador."""


MIN_USUARIO = 3
MAX_USUARIO = 30
MIN_CLAVE = 8


def validar_credenciales(username: str, password: str) -> tuple[str, str]:
    """Reglas de cuenta: sin esto, «1» con clave «1» pasaría sin más."""
    usuario = (username or "").strip()
    clave = password or ""
    if len(usuario) < MIN_USUARIO:
        raise ValidacionError(f"El usuario debe tener al menos {MIN_USUARIO} caracteres.")
    if len(usuario) > MAX_USUARIO:
        raise ValidacionError(f"El usuario no puede pasar de {MAX_USUARIO} caracteres.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", usuario):
        raise ValidacionError("El usuario solo admite letras, números, punto, guion y guion bajo.")
    if len(clave) < MIN_CLAVE:
        raise ValidacionError(f"La contraseña debe tener al menos {MIN_CLAVE} caracteres.")
    if clave.isdigit() or clave.isalpha():
        raise ValidacionError("La contraseña debe combinar letras y números.")
    if clave.lower() == usuario.lower():
        raise ValidacionError("La contraseña no puede ser igual al usuario.")
    return usuario, clave


def validar_citas(datos: dict) -> dict:
    """Comprueba los datos de citas y devuelve los valores limpios.

    Las reglas salen del dominio declarado: tipos, obligatoriedad y rangos.
    """
    limpio = dict(datos)
    if datos.get('cliente') in (None, ''):
        raise ValidacionError('Cliente es obligatorio.')
    if datos.get('cliente') is not None:
        limpio['cliente'] = str(datos.get('cliente')).strip()
    if datos.get('sede') in (None, ''):
        raise ValidacionError('Sede es obligatorio.')
    if datos.get('sede') is not None:
        limpio['sede'] = str(datos.get('sede')).strip()
    if datos.get('barbero') in (None, ''):
        raise ValidacionError('Barbero es obligatorio.')
    if datos.get('barbero') is not None:
        limpio['barbero'] = str(datos.get('barbero')).strip()
    if datos.get('servicio') in (None, ''):
        raise ValidacionError('Servicio es obligatorio.')
    if datos.get('servicio') is not None:
        limpio['servicio'] = str(datos.get('servicio')).strip()
    if datos.get('fecha') in (None, ''):
        raise ValidacionError('Fecha es obligatorio.')
    if datos.get('fecha') is not None:
        limpio['fecha'] = str(datos.get('fecha')).strip()
    if datos.get('hora') in (None, ''):
        raise ValidacionError('Hora es obligatorio.')
    if datos.get('hora') not in (None, '') and datos.get('hora') not in ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '18:00']:
        raise ValidacionError('Hora debe ser una de: ' + ', '.join(['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '18:00']))
    if datos.get('estado') in (None, ''):
        raise ValidacionError('Estado es obligatorio.')
    if datos.get('estado') not in (None, '') and datos.get('estado') not in ['pendiente', 'confirmada', 'atendida', 'cancelada']:
        raise ValidacionError('Estado debe ser una de: ' + ', '.join(['pendiente', 'confirmada', 'atendida', 'cancelada']))
    if datos.get('monto') in (None, ''):
        raise ValidacionError('Monto cobrado (solo si fue atendida) es obligatorio.')
    if datos.get('monto') not in (None, ''):
        try:
            limpio['monto'] = float(datos.get('monto'))
        except (TypeError, ValueError):
            raise ValidacionError('Monto cobrado (solo si fue atendida) debe ser un número.')
    if limpio.get('monto') is not None and limpio['monto'] < 0.0:
        raise ValidacionError('Monto cobrado (solo si fue atendida) no puede ser menor que 0.')
    return limpio


class AuthService:
    def __init__(self, users: UserRepository, hasher: PasswordHasher, tokens: TokenService) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def register(self, username: str, password: str) -> User:
        usuario, clave = validar_credenciales(username, password)
        if self._users.by_username(usuario):
            raise AuthError("Ese usuario ya está registrado")
        return self._users.create(usuario, self._hasher.hash(clave))

    def login(self, username: str, password: str) -> str:
        hashed = self._users.hashed_password(username)
        if not hashed or not self._hasher.verify(password, hashed):
            raise AuthError("Usuario o contraseña incorrectos")
        return self._tokens.issue(username)

    def user_from_token(self, token: str) -> User | None:
        username = self._tokens.username_from(token)
        return self._users.by_username(username) if username else None


#: Campos de citas que apuntan a un catálogo. El valor debe
#: existir allí: sin esta comprobación, el desplegable del frontend sería pura
#: decoración (con la API a mano se podría guardar cualquier cosa).
RELACIONES: dict[str, str] = {'cliente': 'clientes', 'sede': 'sedes', 'barbero': 'barberos'}

#: Definición de los campos de cada catálogo, para validar las altas del admin.
CAMPOS_CATALOGOS: dict = {'sedes': [{'nombre': 'nombre', 'etiqueta': 'Sede', 'tipo': 'texto', 'obligatorio': True, 'opciones': [], 'minimo': None, 'maximo': None}, {'nombre': 'direccion', 'etiqueta': 'Dirección', 'tipo': 'texto', 'obligatorio': True, 'opciones': [], 'minimo': None, 'maximo': None}, {'nombre': 'telefono', 'etiqueta': 'Teléfono', 'tipo': 'texto', 'obligatorio': True, 'opciones': [], 'minimo': None, 'maximo': None}], 'clientes': [{'nombre': 'nombre', 'etiqueta': 'Nombre', 'tipo': 'texto', 'obligatorio': True, 'opciones': [], 'minimo': None, 'maximo': None}, {'nombre': 'telefono', 'etiqueta': 'Teléfono', 'tipo': 'texto', 'obligatorio': True, 'opciones': [], 'minimo': None, 'maximo': None}, {'nombre': 'correo', 'etiqueta': 'Correo', 'tipo': 'texto', 'obligatorio': True, 'opciones': [], 'minimo': None, 'maximo': None}, {'nombre': 'puntos', 'etiqueta': 'Puntos de fidelidad', 'tipo': 'entero', 'obligatorio': True, 'opciones': [], 'minimo': 0.0, 'maximo': None}], 'barberos': [{'nombre': 'nombre', 'etiqueta': 'Nombre', 'tipo': 'texto', 'obligatorio': True, 'opciones': [], 'minimo': None, 'maximo': None}, {'nombre': 'sede', 'etiqueta': 'Sede', 'tipo': 'texto', 'obligatorio': True, 'opciones': [], 'minimo': None, 'maximo': None}, {'nombre': 'comision', 'etiqueta': 'Comisión (%)', 'tipo': 'decimal', 'obligatorio': True, 'opciones': [], 'minimo': 0.0, 'maximo': None}]}


def validar_catalogo(slug: str, datos: dict) -> dict:
    """Valida un ítem de catálogo contra su definición declarada."""
    campos = CAMPOS_CATALOGOS.get(slug)
    if campos is None:
        raise ValidacionError("Ese catálogo no existe.")
    limpio: dict = {}
    for campo in campos:
        bruto = datos.get(campo["nombre"])
        vacio = bruto is None or str(bruto).strip() == ""
        if campo["obligatorio"] and vacio:
            raise ValidacionError(campo["etiqueta"] + " es obligatorio.")
        if vacio:
            continue
        if campo["tipo"] in ("entero", "decimal"):
            try:
                numero = int(bruto) if campo["tipo"] == "entero" else float(bruto)
            except (TypeError, ValueError):
                raise ValidacionError(campo["etiqueta"] + " debe ser un número.")
            if campo["minimo"] is not None and numero < campo["minimo"]:
                raise ValidacionError(campo["etiqueta"] + " es demasiado pequeño.")
            if campo["maximo"] is not None and numero > campo["maximo"]:
                raise ValidacionError(campo["etiqueta"] + " es demasiado grande.")
            limpio[campo["nombre"]] = numero
        elif campo["tipo"] == "opcion":
            if str(bruto) not in campo["opciones"]:
                raise ValidacionError(campo["etiqueta"] + " debe ser una de: " + ", ".join(campo["opciones"]))
            limpio[campo["nombre"]] = str(bruto)
        elif campo["tipo"] == "booleano":
            limpio[campo["nombre"]] = bool(bruto)
        else:
            limpio[campo["nombre"]] = str(bruto).strip()[:500]
    return limpio


class CatalogoService:
    """Lo que administra el dueño: consultar es de todos, tocar es del admin."""

    def __init__(self, repo: CatalogoRepository) -> None:
        self._repo = repo

    def listar_todos(self) -> dict:
        return {slug: self._repo.listar(slug) for slug in CAMPOS_CATALOGOS}

    def crear(self, user: User, slug: str, datos: dict) -> dict:
        if not user.es_admin:
            raise PermisoError("Solo el administrador puede modificar los catálogos.")
        return self._repo.crear(slug, validar_catalogo(slug, datos))

    def borrar(self, user: User, slug: str, item_id: int) -> bool:
        if not user.es_admin:
            raise PermisoError("Solo el administrador puede modificar los catálogos.")
        if slug not in CAMPOS_CATALOGOS:
            raise ValidacionError("Ese catálogo no existe.")
        return self._repo.borrar(slug, item_id)


class CitaService:
    def __init__(self, repo: CitaRepository, catalogos: CatalogoRepository | None = None) -> None:
        self._repo = repo
        self._catalogos = catalogos

    def _validar_relaciones(self, datos: dict) -> dict:
        for campo, slug in RELACIONES.items():
            valor = datos.get(campo)
            if valor and self._catalogos is not None and not self._catalogos.existe_valor(slug, str(valor)):
                raise ValidacionError(f"'{valor}' no está en el catálogo. Elige una de las opciones.")
        return datos

    def list_para(self, user: User) -> list[tuple[Cita, str | None]]:
        """Lo que este usuario tiene derecho a ver.

        El administrador ve TODO y con el nombre de cada dueño: es la dueña del
        negocio mirando su agenda, no un usuario más mirando la suya.
        """
        if user.es_admin:
            return [(r, dueno) for r, dueno in self._repo.list_all()]
        return [(r, None) for r in self._repo.list_for(user.id)]

    def create(self, owner_id: int, datos: dict) -> Cita:
        return self._repo.create(owner_id, self._validar_relaciones(validar_citas(datos)))

    def update_como(self, user: User, registro_id: int, datos: dict) -> Cita | None:
        """El admin corrige el registro de cualquiera; los demás, solo el suyo.

        Tiene que ser simétrico con `delete_como`: si el administrador ve todos
        los registros y puede cancelarlos, no poder CORREGIR uno sería una
        asimetría sin explicación — vería la errata y no podría tocarla.
        """
        limpio = self._validar_relaciones(validar_citas(datos))
        if user.es_admin:
            return self._repo.update_any(registro_id, limpio)
        return self._repo.update(registro_id, user.id, limpio)

    def delete_como(self, user: User, registro_id: int) -> bool:
        """El admin puede cancelar el registro de cualquiera; los demás, el suyo."""
        if user.es_admin:
            return self._repo.delete_any(registro_id)
        return self._repo.delete(registro_id, user.id)

    def resumen_para(self, user: User) -> dict:
        """Los números que acompañan a la lista, sobre lo que este usuario VE."""
        registros = [r for r, _ in self.list_para(user)]
        resultado: dict = {}
        resultado['Citas registradas'] = len(registros)
        valores = [getattr(r, 'monto') for r in registros if getattr(r, 'monto', None) is not None]
        resultado['Total facturado (citas atendidas)'] = sum(valores) if valores else 0
        valores = [getattr(r, 'monto') for r in registros if getattr(r, 'monto', None) is not None]
        resultado['Cobro más alto'] = max(valores) if valores else 0
        return resultado
