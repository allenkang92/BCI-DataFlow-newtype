from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
from fastapi.responses import HTMLResponse

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

@router.get("/add/{session_id}", response_class=HTMLResponse)
async def add_data_point_form(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return templates.TemplateResponse("add_data_point.html", {"request": request, "session": session})

@router.post("/add/{session_id}", response_class=HTMLResponse)
async def add_data_point(request: Request, session_id: int, db: Session = Depends(get_db)):
    form = await request.form()
    data_point = schemas.BCIDataCreate(
        timestamp=datetime.now(),
        channel_1=float(form.get("channel_1")),
        channel_2=float(form.get("channel_2")),
        channel_3=float(form.get("channel_3")),
        channel_4=float(form.get("channel_4"))
    )
    crud.create_data_point(db, data_point, session_id)
    return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)

@router.post("/{data_id}/delete", response_class=HTMLResponse)
async def delete_data_point(request: Request, data_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_data_point(db, data_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Data point not found")
    return RedirectResponse(url=request.headers.get("referer"), status_code=303)