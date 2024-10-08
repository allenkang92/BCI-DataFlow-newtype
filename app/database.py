from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# SQLite 데이터베이스 URL 설정
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL  # "sqlite:///Users/c-26/BCI-DataFlow-mlops/database.db" 형식으로 설정

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite는 스레드에서 데이터베이스 연결을 공유하지 않도록 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
