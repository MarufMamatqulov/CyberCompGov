from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://cybercomp:cybercomp@db:5432/cybercomp"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720
    admin_password: str = "Admin@2026"
    officer_password: str = "Demo@2026"
    # Himoya namoyishi uchun 1-click kirish va OneID/E-IMZO simulyatsiyasi
    demo_mode: bool = True
    eimzo_demo_pin: str = "123456"
    public_base_url: str = "http://localhost"
    cors_origins: str = "*"
    seed_on_startup: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
