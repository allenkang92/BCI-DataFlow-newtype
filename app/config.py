# app/config.py 수정
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCI-Data-Flow"
    API_V1_STR: str = "/api/v1"

    # 기존 MySQL 설정 제거하고 SQLite 사용
    DATABASE_URL: str = "sqlite:///./sql_app.db"  # SQLite 데이터베이스 URL

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
