from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app import crud, models, schemas
from app.database import engine, get_db
from app.config import settings
from app.routers import bci_sessions, bci_data

from sqlalchemy.orm import Session
import os
from pathlib import Path  # 경로 관리를 위해 Path 사용

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# BASE_DIR을 더 안전하게 설정 (Pathlib 사용)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# 정적 파일 경로 설정 (Pathlib을 사용하여 경로 안전성 강화)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# 라우터 설정
app.include_router(bci_sessions.router, prefix=settings.API_V1_STR, tags=["sessions"])
app.include_router(bci_data.router, prefix=settings.API_V1_STR, tags=["data"])

# 루트 경로 - 세션 리스트 페이지
@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db)
    return templates.TemplateResponse("session_list.html", {"request": request, "sessions": sessions})

# 데이터 포인트 추가 페이지
@app.get("/add-data-point/{session_id}", response_class=HTMLResponse)
async def add_data_point(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    return templates.TemplateResponse("add_data_point.html", {"request": request, "session": session})

# 세션 생성 페이지
@app.get("/create-session", response_class=HTMLResponse)
async def create_session(request: Request):
    return templates.TemplateResponse("create_session.html", {"request": request})

# 대시보드 페이지 - 세션 리스트를 보여줌
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db)
    return templates.TemplateResponse("dashboard.html", {"request": request, "sessions": sessions})

# 데이터 포인트 삭제 페이지
@app.get("/delete-data-point/{data_id}", response_class=HTMLResponse)
async def delete_data_point(request: Request, data_id: int, db: Session = Depends(get_db)):
    data_point = crud.get_data_point(db, data_id)
    return templates.TemplateResponse("delete_data_point.html", {"request": request, "data_point": data_point})

# 세션 삭제 페이지
@app.get("/delete-session/{session_id}", response_class=HTMLResponse)
async def delete_session(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    return templates.TemplateResponse("delete_session.html", {"request": request, "session": session})

# 세션 상세 페이지
@app.get("/session-detail/{session_id}", response_class=HTMLResponse)
async def session_detail(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    data_points = crud.get_data_points(db, session_id)
    return templates.TemplateResponse("session_detail.html", {"request": request, "session": session, "data_points": data_points})

# 세션 리스트 페이지
@app.get("/session-list", response_class=HTMLResponse)
async def session_list(request: Request, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db)
    return templates.TemplateResponse("session_list.html", {"request": request, "sessions": sessions})
