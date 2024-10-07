from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter()

@router.post("/sessions/", response_model=schemas.BCISession)
def create_session(session: schemas.BCISessionCreate, db: Session = Depends(get_db)):
    return crud.create_session(db=db, session=session)

@router.get("/sessions/", response_model=list[schemas.BCISession])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db, skip=skip, limit=limit)
    return sessions

@router.get("/sessions/{session_id}", response_model=schemas.BCISession)
def read_session(session_id: int, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.post("/sessions/{session_id}/data/", response_model=schemas.BCIData)
def create_data_for_session(
    session_id: int, data_point: schemas.BCIDataCreate, db: Session = Depends(get_db)
):
    return crud.create_data_point(db=db, data_point=data_point, session_id=session_id)

@router.get("/sessions/{session_id}/data/", response_model=list[schemas.BCIData])
def read_data_points(session_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data_points = crud.get_data_points(db, session_id=session_id, skip=skip, limit=limit)
    return data_points