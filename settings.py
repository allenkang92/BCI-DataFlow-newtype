from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCI-DataFlow"
    API_V1_STR: str = "/api/v1"

    MYSQL_SERVER: str  # MySQL 서버 주소
    MYSQL_USER: str    # MySQL 사용자
    MYSQL_PASSWORD: str  # MySQL 비밀번호
    MYSQL_DB: str      # 사용할 데이터베이스 이름
    DATABASE_URL: str  # MySQL 연결 문자열

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 이미 .env에 DATABASE_URL이 설정되어 있는지 확인 후, 없을 경우 기본 설정
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}/{self.MYSQL_DB}"

settings = Settings()
