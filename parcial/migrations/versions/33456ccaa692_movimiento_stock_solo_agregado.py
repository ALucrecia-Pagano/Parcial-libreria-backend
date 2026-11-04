"""movimiento stock solo agregado

Migración escrita a mano (sin --autogenerate) y leída antes de aplicarla:
la comparación automática de Alembic mira tablas, columnas e índices, pero
no detecta funciones PL/pgSQL ni disparadores (RN-12).

El disparador rechaza UPDATE y DELETE fila por fila. TRUNCATE no lo activa,
y por eso seed.py puede vaciar la tabla.

Revision ID: 33456ccaa692
Revises: be806bc23837
Create Date: 2026-11-04 09:52:30.284971

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '33456ccaa692'
down_revision: Union[str, None] = 'be806bc23837'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Dos op.execute separados: asyncpg no acepta varias sentencias en un
    # mismo comando preparado.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION rechazar_modificacion_movimiento_stock()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'movimiento_stock es de sólo agregado: no se permite % sobre sus filas (RN-12)', TG_OP;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_movimiento_stock_solo_agregado
        BEFORE UPDATE OR DELETE ON movimiento_stock
        FOR EACH ROW
        EXECUTE FUNCTION rechazar_modificacion_movimiento_stock();
        """
    )


def downgrade() -> None:
    # Primero el disparador, porque depende de la función.
    op.execute("DROP TRIGGER IF EXISTS trg_movimiento_stock_solo_agregado ON movimiento_stock;")
    op.execute("DROP FUNCTION IF EXISTS rechazar_modificacion_movimiento_stock();")
