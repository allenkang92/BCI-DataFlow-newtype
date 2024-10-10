from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCI-DataFlow"
    API_V1_STR: str = "/api/v1"

    # SQLite 설정
    DATABASE_URL: str

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
