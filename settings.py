from pydantic import BaseSettings, MySQLDsn
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCI-DataFlow"
    API_V1_STR: str = "/api/v1"

    # MySQL 설정 추가
    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    DATABASE_URL: Optional[MySQLDsn] = None

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = MySQLDsn.build(
                scheme="mysql",
                user=self.MYSQL_USER,
                password=self.MYSQL_PASSWORD,
                host=self.MYSQL_SERVER,
                path=f"/{self.MYSQL_DB}",
            )

settings = Settings()
