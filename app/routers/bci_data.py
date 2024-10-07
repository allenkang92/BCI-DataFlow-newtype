from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter()

@router.get("/data/{data_id}", response_model=schemas.BCIData)
def read_data_point(data_id: int, db: Session = Depends(get_db)):
    data_point = crud.get_data_point(db, data_id=data_id)
    if data_point is None:
        raise HTTPException(status_code=404, detail="Data point not found")
    return data_point

@router.put("/data/{data_id}", response_model=schemas.BCIData)
def update_data_point(data_id: int, data_point: schemas.BCIDataCreate, db: Session = Depends(get_db)):
    updated_data = crud.update_data_point(db, data_id=data_id, data_point=data_point)
    if updated_data is None:
        raise HTTPException(status_code=404, detail="Data point not found")
    return updated_data

@router.delete("/data/{data_id}")
def delete_data_point(data_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_data_point(db, data_id=data_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Data point not found")
    return {"message": "Data point deleted successfully"}