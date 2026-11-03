"""DTOs de entrada y salida del módulo ventas."""

from datetime import datetime
from decimal import Decimal

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel


class RenglonCreate(SQLModel):
    libro_id: int
    cantidad: int = Field(gt=0)


class VentaCreate(SQLModel):
    cliente_id: int
    renglones: list[RenglonCreate] = Field(min_length=1)

    @field_validator("renglones")
    @classmethod
    def validar_libros_unicos(cls, renglones: list[RenglonCreate]) -> list[RenglonCreate]:
        libros_ids = [renglon.libro_id for renglon in renglones]
        if len(libros_ids) != len(set(libros_ids)):
            raise ValueError("No se puede repetir un libro en la venta")
        return renglones


class VentaRead(SQLModel):
    id: int
    cliente_id: int
    fecha: datetime
    total: Decimal


class ClienteVentaRead(SQLModel):
    id: int
    nombre: str
    email: str


class RenglonRead(SQLModel):
    libro_id: int
    titulo: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    @model_validator(mode="before")
    @classmethod
    def completar_renglon(cls, renglon):
        if isinstance(renglon, dict):
            return renglon
        return {
            "libro_id": renglon.libro_id,
            "titulo": renglon.libro.titulo,
            "cantidad": renglon.cantidad,
            "precio_unitario": renglon.precio_unitario,
            "subtotal": renglon.cantidad * renglon.precio_unitario,
        }


class VentaDetalleRead(SQLModel):
    id: int
    fecha: datetime
    total: Decimal
    cliente: ClienteVentaRead
    renglones: list[RenglonRead]
