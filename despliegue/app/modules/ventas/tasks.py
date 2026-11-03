"""Simulación asincrónica del aviso de comprobante (sin usar la sesión)."""
import asyncio
import logging

logger = logging.getLogger("uvicorn.error")


async def avisar_comprobante(venta_id: int, email: str) -> None:
    await asyncio.sleep(0.5)
    logger.info("Comprobante de venta %s enviado a %s (simulado)", venta_id, email)
