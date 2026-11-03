"""Configuración central de la aplicación.

Lee variables de entorno desde `.env` (ver `.env.example`).
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "TP Libreria API")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL.strip():
        raise RuntimeError(
            "Falta configurar DATABASE_URL en el entorno o en .env "
            "(ver .env.example)"
        )


settings = Settings()
