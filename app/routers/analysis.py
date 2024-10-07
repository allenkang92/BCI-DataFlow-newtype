from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
from ..analysis import generate_session_plots
import io
import base64

router = APIRouter()

@router.get("/analysis/session/{session_id}")
def analyze_session(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data_points = crud.get_data_points(db, session_id=session_id)
    
    timeseries_plot, heatmap_plot = generate_session_plots(session, data_points)
    
    return {
        "session_id": session_id,
        "timeseries_plot": base64.b64encode(timeseries_plot.getvalue()).decode(),
        "heatmap_plot": base64.b64encode(heatmap_plot.getvalue()).decode()
    }