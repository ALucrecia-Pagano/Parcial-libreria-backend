"""Carga inicial para C-01 a C-08. Ejecutar en una base migrada y vacía."""
import asyncio
from decimal import Decimal
from sqlalchemy import func
from sqlmodel import select
from app.core.database import init_resources, dispose_resources
from app.modules.autores.models import Autor
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro, LibroAutor
from app.modules.ventas.models import Venta, RenglonVenta


async def seed():
    _, factory = init_resources()
    try:
        async with factory() as session:
            for model in (Editorial, Genero, Autor, Libro, Cliente, Venta):
                if await session.scalar(select(func.count()).select_from(model)):
                    raise RuntimeError("La carga inicial requiere una base vacía; no se borraron datos")
            editorial = Editorial(nombre="Editorial de prueba", pais="Argentina")
            genero = Genero(nombre="Novela")
            autores = [Autor(nombre="Julio Cortázar", nacionalidad="Argentina"),
                       Autor(nombre="Adolfo Bioy Casares", nacionalidad="Argentina"),
                       Autor(nombre="Silvina Ocampo", nacionalidad="Argentina")]
            cliente = Cliente(nombre="Mateo", email="mismo_email@example.com",
                              perfil=PerfilCliente(telefono="123456789", direccion="Calle Falsa 123"))
            session.add_all([editorial, genero, *autores, cliente])
            await session.flush()
            libro1 = Libro(isbn="978-950-00-0001-1", titulo="Rayuela", precio=Decimal("25000.00"),
                           stock=10, editorial_id=editorial.id, genero_id=genero.id,
                           autorias=[LibroAutor(autor_id=autores[0].id, rol="autor", orden=1)])
            libro2 = Libro(isbn="978-950-00-0006-6", titulo="Los que aman, odian", precio=Decimal("21000.00"),
                           stock=4, editorial_id=editorial.id, genero_id=genero.id,
                           autorias=[LibroAutor(autor_id=autores[1].id, rol="coautor", orden=1),
                                     LibroAutor(autor_id=autores[2].id, rol="coautor", orden=2)])
            session.add_all([libro1, libro2])
            await session.flush()
            venta = Venta(cliente_id=cliente.id, total=Decimal("71000.00"), renglones=[
                RenglonVenta(libro_id=libro1.id, cantidad=2, precio_unitario=libro1.precio),
                RenglonVenta(libro_id=libro2.id, cantidad=1, precio_unitario=libro2.precio)])
            session.add(venta)
            await session.commit()
            print(f"Datos iniciales: cliente={cliente.id}, libros={libro1.id},{libro2.id}, venta={venta.id}")
    finally:
        await dispose_resources()


if __name__ == "__main__":
    asyncio.run(seed())
