from pydantic import BaseSettings, AnyUrl
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCI-Data-Flow"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: AnyUrl = "sqlite:///./mlruns/test.db"  # SQLite 기본값으로 설정

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
