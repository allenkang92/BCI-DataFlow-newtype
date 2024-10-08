from pydantic import BaseSettings, MySQLDsn
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCI-Data-Flow"
    API_V1_STR: str = "/api/v1"

    MYSQL_SERVER: str  # MySQL 서버 주소
    MYSQL_USER: str    # MySQL 사용자
    MYSQL_PASSWORD: str  # MySQL 비밀번호
    MYSQL_DB: str      # 사용할 데이터베이스 이름
    DATABASE_URL: Optional[MySQLDsn] = None  # MySQL 데이터베이스 URL

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
                scheme="mysql+pymysql",  # MySQL을 위한 스키마
                user=self.MYSQL_USER,
                password=self.MYSQL_PASSWORD,
                host=self.MYSQL_SERVER,
                path=f"/{self.MYSQL_DB}",
            )

settings = Settings()
