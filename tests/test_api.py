from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app, get_db
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_session():
    response = client.post(
        "/api/v1/sessions/",
        json={"session_name": "Test Session", "date_recorded": "2023-01-01T00:00:00", "subject_id": "subject1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_name"] == "Test Session"
    assert "id" in data

def test_read_sessions():
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Add more tests for other endpoints