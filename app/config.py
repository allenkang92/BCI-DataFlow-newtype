from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCI-DataFlow"
    API_V1_STR: str = "/api/v1"

    # MySQL 설정
    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    DATABASE_URL: str  # 직접 URL을 문자열로 처리

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
