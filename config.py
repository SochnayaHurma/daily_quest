from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent


class PostgresSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str


class Settings(BaseSettings):
    db_settings: PostgresSettings = PostgresSettings()
    SECRET_KEY: str
    TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    TOKEN_ALGORITHM: str = 'HS256'
    DEBUG: bool = True

    CONTRACT_COOKIE_NAME: str = 'contract_id'


settings = Settings()

if settings.DEBUG:
    from dotenv import load_dotenv
    load_dotenv()
