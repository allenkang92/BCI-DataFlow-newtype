from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app import crud, models, schemas
from app.database import engine
from app.config import settings
from app.routers import bci_sessions, bci_data

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(bci_sessions.router, prefix=settings.API_V1_STR, tags=["sessions"])
app.include_router(bci_data.router, prefix=settings.API_V1_STR, tags=["data"])

@app.get("/")
async def root():
    return {"message": "Welcome to BCI-DataFlow API"}

@app.get("/add-data-point", response_class=HTMLResponse)
async def add_data_point(request: Request):
    return templates.TemplateResponse("add_data_point.html", {"request": request})

@app.get("/create-session", response_class=HTMLResponse)
async def create_session(request: Request):
    return templates.TemplateResponse("create_session.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/delete-data-point", response_class=HTMLResponse)
async def delete_data_point(request: Request):
    return templates.TemplateResponse("delete_data_point.html", {"request": request})

@app.get("/delete-session", response_class=HTMLResponse)
async def delete_session(request: Request):
    return templates.TemplateResponse("delete_session.html", {"request": request})

@app.get("/session-detail", response_class=HTMLResponse)
async def session_detail(request: Request):
    return templates.TemplateResponse("session_detail.html", {"request": request})

@app.get("/session-list", response_class=HTMLResponse)
async def session_list(request: Request):
    return templates.TemplateResponse("session_list.html", {"request": request})