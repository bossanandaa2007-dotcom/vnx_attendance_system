from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.schemas.attendance_schema import AttendanceMark, AttendanceSessionCreate
from app.services.attendance_service import mark_attendance
from app.utils.time_utils import today_local

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/session/start")
def start_session(payload: AttendanceSessionCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["session_date"] = data["session_date"] or today_local()
    session = AttendanceSession(**data, status="active")
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"success": True, "message": "Session started", "data": session}


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    return {"success": True, "message": "Sessions fetched", "data": db.query(AttendanceSession).order_by(AttendanceSession.created_at.desc()).all()}


@router.get("/session/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    item = db.get(AttendanceSession, session_id)
    if not item:
        raise HTTPException(404, "Session not found")
    return {"success": True, "message": "Session fetched", "data": item}


@router.post("/session/{session_id}/complete")
def complete_session(session_id: int, db: Session = Depends(get_db)):
    item = db.get(AttendanceSession, session_id)
    if not item:
        raise HTTPException(404, "Session not found")
    item.status = "completed"
    db.commit()
    return {"success": True, "message": "Session completed", "data": item}


@router.post("/mark")
def mark(payload: AttendanceMark, db: Session = Depends(get_db)):
    record, message = mark_attendance(db, payload)
    if not record:
        raise HTTPException(404, message)
    return {"success": True, "message": message, "data": record}


@router.post("/mark-absent")
def mark_absent(payload: AttendanceMark, db: Session = Depends(get_db)):
    payload.recognition_method = "auto_absent"
    record, message = mark_attendance(db, payload)
    if record:
        record.status = "absent"
        db.commit()
    return {"success": bool(record), "message": message, "data": record}


@router.get("/today")
def today(db: Session = Depends(get_db)):
    rows = db.query(AttendanceRecord).filter(AttendanceRecord.attendance_date == today_local()).all()
    return {"success": True, "message": "Today attendance fetched", "data": rows}


@router.get("/by-date")
def by_date(attendance_date: str, db: Session = Depends(get_db)):
    rows = db.query(AttendanceRecord).filter(AttendanceRecord.attendance_date == attendance_date).all()
    return {"success": True, "message": "Attendance fetched", "data": rows}


@router.get("/by-person/{person_id}")
def by_person(person_id: int, db: Session = Depends(get_db)):
    return {"success": True, "message": "Attendance fetched", "data": db.query(AttendanceRecord).filter(AttendanceRecord.person_id == person_id).all()}


@router.get("/session/{session_id}/records")
def session_records(session_id: int, db: Session = Depends(get_db)):
    return {"success": True, "message": "Records fetched", "data": db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()}
