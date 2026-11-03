"""Contratos de autores, separados de la tabla."""
from pydantic import model_validator
from sqlmodel import Field, SQLModel


class AutorCreate(SQLModel):
    nombre: str = Field(min_length=1)
    nacionalidad: str = Field(min_length=1)


class AutorRead(AutorCreate):
    id: int


class AutorUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    nacionalidad: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def rechazar_nulos(self):
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Los campos del autor no pueden ser nulos")
        return self
