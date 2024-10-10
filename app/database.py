from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# SQLite 데이터베이스 URL 설정
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# SQLite용 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 세션 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 기본 베이스 클래스
Base = declarative_base()

# 데이터베이스 연결 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
