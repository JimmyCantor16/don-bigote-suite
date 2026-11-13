"""Dominio: entidades puras. NO importan FastAPI ni SQLAlchemy."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class User:
    id: int | None
    username: str
    #: El administrador es el dueño del negocio: ve todos los registros y
    #: gestiona los catálogos. Los demás solo ven y tocan lo suyo.
    es_admin: bool = False


@dataclass
class Cita:
    """Un registro de citas."""

    id: int | None
    cliente: str
    sede: str
    barbero: str
    servicio: str
    fecha: str
    hora: str
    estado: str
    monto: float
    owner_id: int
