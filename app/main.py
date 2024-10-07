from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app import crud, models, schemas
from app.database import engine, get_db
from app.config import settings
from app.routers import bci_sessions, bci_data
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

templates = Jinja2Templates(directory="/code/templates")
app.mount("/static", StaticFiles(directory="/code/static"), name="static")

app.include_router(bci_sessions.router, prefix=settings.API_V1_STR, tags=["sessions"])
app.include_router(bci_data.router, prefix=settings.API_V1_STR, tags=["data"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db)
    return templates.TemplateResponse("session_list.html", {"request": request, "sessions": sessions})

@app.get("/add-data-point/{session_id}", response_class=HTMLResponse)
async def add_data_point(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    return templates.TemplateResponse("add_data_point.html", {"request": request, "session": session})

@app.get("/create-session", response_class=HTMLResponse)
async def create_session(request: Request):
    return templates.TemplateResponse("create_session.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db)
    return templates.TemplateResponse("dashboard.html", {"request": request, "sessions": sessions})

@app.get("/delete-data-point/{data_id}", response_class=HTMLResponse)
async def delete_data_point(request: Request, data_id: int, db: Session = Depends(get_db)):
    data_point = crud.get_data_point(db, data_id)
    return templates.TemplateResponse("delete_data_point.html", {"request": request, "data_point": data_point})

@app.get("/delete-session/{session_id}", response_class=HTMLResponse)
async def delete_session(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    return templates.TemplateResponse("delete_session.html", {"request": request, "session": session})

@app.get("/session-detail/{session_id}", response_class=HTMLResponse)
async def session_detail(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    data_points = crud.get_data_points(db, session_id)
    return templates.TemplateResponse("session_detail.html", {"request": request, "session": session, "data_points": data_points})

@app.get("/session-list", response_class=HTMLResponse)
async def session_list(request: Request, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db)
    return templates.TemplateResponse("session_list.html", {"request": request, "sessions": sessions})