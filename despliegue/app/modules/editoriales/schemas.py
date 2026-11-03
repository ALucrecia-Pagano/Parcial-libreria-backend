"""DTOs del módulo editoriales: entrada (Create, Update) y salida (Read)."""

from typing import Optional

from sqlmodel import Field, SQLModel


class EditorialCreate(SQLModel):
    """Entrada del alta: no lleva id, lo genera la base."""

    nombre: str = Field(min_length=1, max_length=120)
    pais: str = Field(min_length=1, max_length=80)


class EditorialUpdate(SQLModel):
    """Entrada del PATCH: todo opcional, se aplica solo lo enviado."""

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=120)
    pais: Optional[str] = Field(default=None, min_length=1, max_length=80)


class EditorialRead(SQLModel):
    """Salida: lo que la API devuelve al cliente."""

    id: int
    nombre: str
    pais: str