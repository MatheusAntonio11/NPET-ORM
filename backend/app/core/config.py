"""
Configuração global da aplicação.

Carrega as variáveis de ambiente (arquivo `.env`) usando Pydantic Settings. Use sempre `from app.core.config import settings` para ler configurações.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "NPET API"
    APP_ENV: str = "development"
    PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    DATABASE_URL: str

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instância única de Settings (cacheada)."""
    return Settings()


settings = get_settings()
