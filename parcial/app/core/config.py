"""Configuración central de la aplicación.

Las variables se leen del entorno y, en local, del archivo `.env` (ver
`env.example`). `POSTGRES_PASSWORD` y `JWT_SECRET` NO tienen valor por defecto:
si faltan, `Settings()` lanza `ValidationError` al importar este módulo, y por
eso fallan tanto `uvicorn` como `alembic`.

Nunca loguear ni imprimir `settings` entero ni `settings.model_dump()`:
`DATABASE_URL` lleva la contraseña en claro.
"""

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,  # el ValidationError no muestra los valores (secretos)
    )

    APP_NAME: str = "Parcial Librería API"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr  # sin default
    POSTGRES_DB: str = "libreria"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    JWT_SECRET: SecretStr  # sin default
    JWT_MINUTOS: int = 30
    BCRYPT_COSTO: int = 12
    COOKIE_SECURE: bool = False

    DB_POOL_SIZE: int = 5
    SQL_ECHO: bool = False

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # URL.create escapa @, / y : de la contraseña (un f-string los rompería).
        return URL.create(
            "postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)


settings = Settings()
