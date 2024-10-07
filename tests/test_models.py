import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import BCISession, BCIData, User
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_bci_session(db_session):
    session = BCISession(session_name="Test Session", date_recorded=datetime.now(), subject_id="subject1")
    db_session.add(session)
    db_session.commit()
    assert session.id is not None
    assert session.session_name == "Test Session"

def test_create_bci_data(db_session):
    session = BCISession(session_name="Test Session", date_recorded=datetime.now(), subject_id="subject1")
    db_session.add(session)
    db_session.commit()

    data = BCIData(session_id=session.id, timestamp=datetime.now(), channel_1=1.0, channel_2=2.0, channel_3=3.0, channel_4=4.0)
    db_session.add(data)
    db_session.commit()

    assert data.id is not None
    assert data.session_id == session.id

def test_create_user(db_session):
    user = User(username="testuser", email="test@example.com", hashed_password="hashedpassword")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

# Add more tests as needed