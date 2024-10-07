from sqlalchemy.orm import Session
from . import models, schemas

def get_session(db: Session, session_id: int):
    return db.query(models.BCISession).filter(models.BCISession.id == session_id).first()

def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BCISession).offset(skip).limit(limit).all()

def create_session(db: Session, session: schemas.BCISessionCreate):
    db_session = models.BCISession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_data_points(db: Session, session_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.BCIData).filter(models.BCIData.session_id == session_id).offset(skip).limit(limit).all()

def create_data_point(db: Session, data_point: schemas.BCIDataCreate, session_id: int):
    db_data_point = models.BCIData(**data_point.dict(), session_id=session_id)
    db.add(db_data_point)
    db.commit()
    db.refresh(db_data_point)
    return db_data_point

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user