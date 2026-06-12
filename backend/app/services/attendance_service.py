from sqlalchemy.orm import Session

from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.person import Person
from app.services.sheet_service import sync_attendance_record
from app.utils.time_utils import now_local, today_local


def mark_attendance(db: Session, payload):
    person = None
    if payload.person_id:
        person = db.get(Person, payload.person_id)
    elif payload.person_code:
        person = db.query(Person).filter(Person.person_code == payload.person_code).first()
    if not person:
        return None, "Person not found"

    session = db.get(AttendanceSession, payload.session_id) if payload.session_id else None
    existing = db.query(AttendanceRecord).filter(
        AttendanceRecord.person_id == person.id,
        AttendanceRecord.session_id == payload.session_id,
        AttendanceRecord.attendance_date == today_local(),
    ).first()
    if existing:
        existing.duplicate_flag = True
        db.commit()
        return existing, "Already marked"

    now = now_local()
    if session and session.session_type == "member_visit":
        status = "visited"
    elif payload.recognition_method == "auto_absent":
        status = "absent"
    else:
        status = "present"
        if session and session.grace_time and now.time() > session.grace_time:
            status = "late"
        if session and session.end_time and now.time() > session.end_time:
            status = "absent"

    record = AttendanceRecord(
        session_id=payload.session_id,
        person_id=person.id,
        person_code=person.person_code,
        person_name=person.full_name,
        person_type=person.person_type,
        category_program=person.category_program,
        batch_name=person.batch_name,
        level_class=person.level_class,
        attendance_date=today_local(),
        marked_time=now,
        status=status,
        confidence_score=payload.confidence_score,
        recognition_method=payload.recognition_method,
        device_name=payload.device_name,
        marked_by=payload.marked_by,
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    sync_attendance_record(db, record)
    db.refresh(record)
    return record, "Attendance marked"
