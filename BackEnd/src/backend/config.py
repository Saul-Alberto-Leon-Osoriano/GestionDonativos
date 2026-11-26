"""Configuracion central del backend, cargada desde BackEnd/.env."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Variables de entorno del backend."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "db_donativos_sanpiox"

    jwt_secret: str = "cambia-este-secreto-en-produccion"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    cors_origins: str = "http://localhost:4200,http://127.0.0.1:4200"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origen.strip()
            for origen in self.cors_origins.split(",")
            if origen.strip()
        ]

    @property
    def database_config(self) -> dict[str, object]:
        return {
            "host": self.db_host,
            "port": self.db_port,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": False,
            "use_pure": True,
        }


@lru_cache
def obtener_settings() -> Settings:
    return Settings()
