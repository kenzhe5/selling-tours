from __future__ import annotations

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_DEFAULT_CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:4200",
    "http://localhost:5173",
    "http://localhost:8001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8001",
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./tours.db"
    cors_origins_line: str = Field(default="", validation_alias="CORS_ORIGINS")
    seed_path: str = "../contracts/tours_seed.json"
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")

    @property
    def cors_origins(self) -> list[str]:
        extra = [s.strip() for s in self.cors_origins_line.split(",") if s.strip()]
        return list(dict.fromkeys([*_DEFAULT_CORS_ORIGINS, *extra]))


settings = Settings()
