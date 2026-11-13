"""Puertos: contratos que la aplicación necesita."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import Cita, User


class UserRepository(ABC):
    @abstractmethod
    def by_username(self, username: str) -> User | None: ...
    @abstractmethod
    def create(self, username: str, hashed_password: str) -> User: ...
    @abstractmethod
    def hashed_password(self, username: str) -> str | None: ...


class CitaRepository(ABC):
    @abstractmethod
    def list_for(self, owner_id: int) -> list[Cita]: ...
    @abstractmethod
    def list_all(self) -> list[tuple[Cita, str]]:
        """Todos los registros con el nombre de su dueño (vista del administrador)."""
    @abstractmethod
    def create(self, owner_id: int, datos: dict) -> Cita: ...
    @abstractmethod
    def get(self, registro_id: int, owner_id: int) -> Cita | None: ...
    @abstractmethod
    def update(self, registro_id: int, owner_id: int, datos: dict) -> Cita | None: ...
    @abstractmethod
    def delete(self, registro_id: int, owner_id: int) -> bool: ...
    @abstractmethod
    def update_any(self, registro_id: int, datos: dict) -> Cita | None:
        """Actualiza sin mirar el dueño. SOLO lo usa el administrador."""
    @abstractmethod
    def delete_any(self, registro_id: int) -> bool:
        """Borra sin mirar el dueño. SOLO lo usa el administrador."""


class CatalogoRepository(ABC):
    """Las entidades de apoyo del negocio (lo que administra el dueño)."""

    @abstractmethod
    def listar(self, slug: str) -> list[dict]: ...
    @abstractmethod
    def crear(self, slug: str, datos: dict) -> dict: ...
    @abstractmethod
    def borrar(self, slug: str, item_id: int) -> bool: ...
    @abstractmethod
    def existe_valor(self, slug: str, valor: str) -> bool:
        """¿Hay un ítem cuyo nombre visible sea `valor`? (valida las relaciones)."""


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain: str) -> str: ...
    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool: ...


class TokenService(ABC):
    @abstractmethod
    def issue(self, username: str) -> str: ...
    @abstractmethod
    def username_from(self, token: str) -> str | None: ...
