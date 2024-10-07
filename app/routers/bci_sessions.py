from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import get_db
from fastapi.templating import Jinja2Templates
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="/code/templates")

class SessionForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.session_name: Optional[str] = None
        self.date_recorded: Optional[str] = None
        self.subject_id: Optional[str] = None

    def load_data(self):
        form = await self.request.form()
        self.session_name = form.get("session_name")
        self.date_recorded = form.get("date_recorded")
        self.subject_id = form.get("subject_id")

    def is_valid(self):
        if not self.session_name or not self.date_recorded or not self.subject_id:
            self.errors.append("All fields are required")
        if not self.errors:
            return True
        return False

@router.get("/create", response_class=HTMLResponse)
async def create_session_form(request: Request):
    return templates.TemplateResponse("create_session.html", {"request": request, "form": SessionForm(request)})

@router.post("/create", response_class=HTMLResponse)
async def create_session(request: Request, db: Session = Depends(get_db)):
    form = SessionForm(request)
    await form.load_data()
    if form.is_valid():
        session = schemas.BCISessionCreate(
            session_name=form.session_name,
            date_recorded=datetime.strptime(form.date_recorded, "%Y-%m-%d"),
            subject_id=form.subject_id
        )
        crud.create_session(db, session)
        return RedirectResponse(url="/session-list", status_code=303)
    return templates.TemplateResponse("create_session.html", {"request": request, "form": form})

@router.get("/{session_id}", response_class=HTMLResponse)
async def session_detail(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    data_points = crud.get_data_points(db, session_id)
    return templates.TemplateResponse("session_detail.html", {"request": request, "session": session, "data_points": data_points})

@router.post("/{session_id}/delete", response_class=HTMLResponse)
async def delete_session(request: Request, session_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return RedirectResponse(url="/sessions", status_code=303)