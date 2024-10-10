from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCI-DataFlow"
    API_V1_STR: str = "/api/v1"

    # SQLite 설정을 위한 변수
    DATABASE_URL: str = "sqlite:///./sqlite_data/sql_app.db"  # SQLite 데이터베이스 파일 경로

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
