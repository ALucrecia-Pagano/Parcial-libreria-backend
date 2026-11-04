"""Datos iniciales del parcial: python seed.py desde la raíz de parcial/.

Vacía todas las tablas y carga el dataset que usan los casos de prueba.
Usa TRUNCATE porque un DELETE lo frenaría el disparador de movimiento_stock,
y RESTART IDENTITY para que los ids vuelvan a 1 (los casos usan ids fijos).

Todo corre en una sola transacción: si algo falla, la base queda como estaba.
Es la única excepción a la regla de escribir libro.stock fuera del punto único,
y aun así stock queda igual a la suma de movimientos en los cinco libros.
"""
import asyncio
from decimal import Decimal

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import dispose_resources, init_resources
from app.modules.autores.models import Autor
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro, LibroAutor, MovimientoStock
from app.modules.usuarios.models import AsignacionRol, EventoSeguridad, Usuario
from app.modules.ventas.models import RenglonVenta, Venta

# Contraseña de mentira, común a los cinco usuarios del seed.
PASSWORD_SEED = "Secreto1234!"

TRUNCATE_TODO = text(
    "TRUNCATE TABLE evento_seguridad, intento_acceso, movimiento_stock, "
    "renglon_venta, venta, perfil_cliente, cliente, libro_autor, libro, "
    "autor, genero, editorial, asignacion_rol, usuario "
    "RESTART IDENTITY CASCADE"
)


def _hash_password_seed() -> str:
    return bcrypt.hashpw(
        PASSWORD_SEED.encode("utf-8"),
        bcrypt.gensalt(rounds=settings.BCRYPT_COSTO),
    ).decode("utf-8")


async def _insertar(session: AsyncSession, *filas: object) -> None:
    """Inserta de a una fila, para que los ids salgan en el orden escrito."""
    for fila in filas:
        session.add(fila)
        await session.flush()


async def _cargar_usuarios(session: AsyncSession) -> None:
    password_hash = _hash_password_seed()
    usuarios = [
        ("admin@example.com", "Admin Principal", "ADMIN", False),
        ("admin2@example.com", "Admin Secundario", "ADMIN", False),
        ("vendedor@example.com", "Vendedor Mostrador", "VENDEDOR", False),
        ("ana@example.com", "Ana Paz", "CLIENTE", False),
        ("nuevo@example.com", "Vendedor Nuevo", "VENDEDOR", True),
    ]
    for usuario_id, (email, nombre, rol, debe_cambiar) in enumerate(usuarios, start=1):
        await _insertar(
            session,
            Usuario(
                email=email,
                nombre=nombre,
                password_hash=password_hash,
                activo=True,
                debe_cambiar_password=debe_cambiar,
            ),
            AsignacionRol(usuario_id=usuario_id, rol=rol, otorgada_por=None),
        )


async def _cargar_catalogo(session: AsyncSession) -> None:
    await _insertar(
        session,
        Editorial(nombre="Letras del Río", pais="Argentina"),
        Editorial(nombre="Ediciones del Plata Sur", pais="Argentina"),
        Editorial(nombre="Editorial Sudamérica Austral", pais="Argentina"),
        Genero(nombre="Novela"),
        Genero(nombre="Cuento"),
        Genero(nombre="Antología"),
        Autor(nombre="Julio Cortázar", nacionalidad="Argentina"),
        Autor(nombre="Jorge Luis Borges", nacionalidad="Argentina"),
        Autor(nombre="Silvina Ocampo", nacionalidad="Argentina"),
        Autor(nombre="Adolfo Bioy Casares", nacionalidad="Argentina"),
        Autor(nombre="Ricardo Piglia", nacionalidad="Argentina"),
        Autor(nombre="Juan José Saer", nacionalidad="Argentina"),  # sin libro en el seed
        Libro(isbn="978-950-00-0001-1", titulo="Rayuela",
              precio=Decimal("25000.00"), stock=10, editorial_id=1, genero_id=1),
        Libro(isbn="978-950-00-0002-8", titulo="Antología de la literatura fantástica",
              precio=Decimal("30000.00"), stock=5, editorial_id=2, genero_id=3),
        Libro(isbn="978-950-00-0003-5", titulo="Ficciones",
              precio=Decimal("22000.00"), stock=8, editorial_id=3, genero_id=2),
        Libro(isbn="978-950-00-0004-2", titulo="Respiración artificial",
              precio=Decimal("27000.00"), stock=3, editorial_id=2, genero_id=1),
        Libro(isbn="978-950-00-0005-9", titulo="Bestiario",
              precio=Decimal("18000.00"), stock=1, editorial_id=3, genero_id=2),
        LibroAutor(libro_id=1, autor_id=1, rol="autor", orden=1),
        LibroAutor(libro_id=2, autor_id=2, rol="coautor", orden=1),
        LibroAutor(libro_id=2, autor_id=3, rol="coautor", orden=2),
        LibroAutor(libro_id=2, autor_id=4, rol="coautor", orden=3),
        LibroAutor(libro_id=3, autor_id=2, rol="autor", orden=1),
        LibroAutor(libro_id=4, autor_id=5, rol="autor", orden=1),
        LibroAutor(libro_id=5, autor_id=1, rol="autor", orden=1),
    )


async def _cargar_clientes(session: AsyncSession) -> None:
    await _insertar(
        session,
        Cliente(nombre="Lucía Fernández", email="lucia@example.com", usuario_id=None),
        PerfilCliente(cliente_id=1, telefono="261-4000001",
                      direccion="Av. San Martín 123, Mendoza"),
        Cliente(nombre="Tomás Ríos", email="tomas@example.com", usuario_id=None),
        Cliente(nombre="Ana Paz", email="ana@example.com", usuario_id=4),
    )


async def _cargar_venta_y_movimientos(session: AsyncSession) -> None:
    await _insertar(
        session,
        Venta(cliente_id=1, total=Decimal("69000.00")),
        RenglonVenta(venta_id=1, libro_id=1, cantidad=1,
                     precio_unitario=Decimal("25000.00")),
        RenglonVenta(venta_id=1, libro_id=3, cantidad=2,
                     precio_unitario=Decimal("22000.00")),
    )
    # Admin carga el stock inicial; el vendedor registra las salidas de la venta 1.
    for libro_id, cantidad in ((1, 11), (2, 5), (3, 10), (4, 3), (5, 1)):
        await _insertar(
            session,
            MovimientoStock(libro_id=libro_id, usuario_id=1, cantidad=cantidad,
                            motivo="Stock inicial"),
        )
    for libro_id, cantidad in ((1, -1), (3, -2)):
        await _insertar(
            session,
            MovimientoStock(libro_id=libro_id, venta_id=1, usuario_id=3,
                            cantidad=cantidad, motivo="Venta"),
        )


async def seed() -> None:
    engine, session_maker = init_resources()
    try:
        async with session_maker() as session:
            await session.execute(TRUNCATE_TODO)
            await _cargar_usuarios(session)
            await _cargar_catalogo(session)
            await _cargar_clientes(session)
            await _cargar_venta_y_movimientos(session)
            await _insertar(
                session,
                EventoSeguridad(actor="SISTEMA", accion="Carga de los datos iniciales"),
            )
            await session.commit()
    finally:
        await dispose_resources(engine)
    print(
        "Datos iniciales cargados: 5 usuarios, 3 editoriales, 3 géneros, 6 autores, "
        "5 libros, 3 clientes, venta 1 por 69000.00, 7 movimientos y 1 evento."
    )


if __name__ == "__main__":
    asyncio.run(seed())
