import json
import time
from datetime import datetime
from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attendance import AttendanceSession
from app.models.face_embedding import FaceEmbedding, FaceEnrollment
from app.models.person import Person
from app.schemas.attendance_schema import AttendanceMark
from app.serializers import attendance_record_data, face_enrollment_data, person_data
from app.services.attendance_service import find_today_record, mark_attendance
from app.services.face_service import best_match, build_gallery, check_liveness, confirm_match, detect_faces, model_label, next_step_for
from app.services.quality_service import MESSAGES, check_pose, check_quality
from app.utils.image_utils import decode_base64_image, decode_image_bytes
from app.utils.time_utils import today_local

router = APIRouter(prefix="/face", tags=["Face"])
# Faces smaller than this (pixels) give unreliable embeddings, so they are not matched.
MIN_FACE_SIZE = 50
GALLERY_TTL_SECONDS = 30
SESSION_TTL_SECONDS = 5
gallery_cache = {}
session_cache = {}
marked_today = {}
INSTRUCTIONS = {
    "front": "Look straight",
    "left": "Turn your head slightly to your left",
    "right": "Turn your head slightly to your right",
    "close": "Move face closer",
    "far": "Move face backward",
    "with_specs": "Wear spectacles and look straight",
    None: "Enrollment completed",
}


async def read_face_payload(request: Request):
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("image") or form.get("file")
        image = decode_image_bytes(await file.read()) if file is not None else decode_base64_image(str(form.get("image_base64") or ""))
        return {
            "person_id": int(form.get("person_id")) if form.get("person_id") else None,
            "current_step": str(form.get("current_step") or "front"),
            "has_specs": str(form.get("has_specs", "false")).lower() == "true",
            "session_id": int(form.get("session_id")) if form.get("session_id") else None,
            "course_id": int(form.get("course_id")) if form.get("course_id") else None,
            "batch_id": int(form.get("batch_id")) if form.get("batch_id") else None,
            "device_name": form.get("device_name"),
            "image": image,
        }
    body = await request.json()
    return {
        "person_id": body.get("person_id"),
        "current_step": body.get("current_step", "front"),
        "has_specs": bool(body.get("has_specs", False)),
        "session_id": body.get("session_id"),
        "course_id": body.get("course_id"),
        "batch_id": body.get("batch_id"),
        "device_name": body.get("device_name"),
        "image": decode_base64_image(body.get("image_base64") or ""),
    }


@router.get("/enrollment/users")
def enrollment_users(course_id: int, batch_id: int, db: Session = Depends(get_db)):
    rows = db.query(Person).filter(
        Person.course_id == course_id,
        Person.batch_id == batch_id,
    ).order_by(Person.full_name.asc()).all()
    return {"success": True, "message": "Enrollment users fetched", "data": [person_data(row) for row in rows]}


@router.post("/enrollment/start/{person_id}")
def start_enrollment(person_id: int, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    print("start enrollment person_id", person_id)
    person.face_enrollment_status = "in_progress"
    # Re-enrolling replaces the old reference faces instead of piling new ones on top.
    db.query(FaceEmbedding).filter(FaceEmbedding.person_id == person_id, FaceEmbedding.is_active == True).update({"is_active": False})
    gallery_cache.clear()
    enrollment = db.query(FaceEnrollment).filter(FaceEnrollment.person_id == person_id).order_by(FaceEnrollment.id.desc()).first()
    if enrollment:
        enrollment.enrollment_status = "in_progress"
        enrollment.current_step = "front"
        enrollment.total_steps = 5
        enrollment.completed_steps = 0
        enrollment.quality_score = None
        enrollment.has_specs_reference = False
        enrollment.started_at = datetime.utcnow()
        enrollment.completed_at = None
    else:
        enrollment = FaceEnrollment(
            person_id=person_id,
            enrollment_status="in_progress",
            current_step="front",
            total_steps=5,
            completed_steps=0,
            started_at=datetime.utcnow(),
        )
        db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return {"success": True, "message": "Face enrollment started", "data": face_enrollment_data(enrollment)}


@router.post("/enrollment/frame")
async def enrollment_frame(request: Request, db: Session = Depends(get_db)):
    payload = await read_face_payload(request)
    print("received person_id", payload["person_id"])
    print("received current_step", payload["current_step"])
    person = db.get(Person, payload["person_id"])
    if not person:
        raise HTTPException(404, "Person not found")
    image = payload["image"]
    if image is None:
        return reject("Invalid image", payload["current_step"], "bad", 0)

    try:
        faces = await run_in_threadpool(detect_faces, image)
    except RuntimeError as exc:
        print("embedding saved or not", "not_saved")
        return reject(str(exc), payload["current_step"], "embedding_failed", 0)

    quality = check_quality(image, [face["box"] for face in faces], reject_sunglasses=True)
    print("quality result", quality)
    if not quality["ok"]:
        print("embedding saved or not", "not_saved")
        return reject(quality["warning"], payload["current_step"], quality["quality_status"], 0)

    pose_ok, pose_warning = check_pose(image, quality, payload["current_step"], faces[0]["turn"])
    print("pose result", {"ok": pose_ok, "warning": pose_warning})
    if not pose_ok:
        print("embedding saved or not", "not_saved")
        return reject(pose_warning, payload["current_step"], "bad", 0)

    try:
        live = (await run_in_threadpool(check_liveness, image, [tuple(faces[0]["box"])]))[0]
    except RuntimeError as exc:
        return reject(str(exc), payload["current_step"], "embedding_failed", 0)
    if not live:
        print("embedding saved or not", "not_saved")
        return reject(MESSAGES["spoof"], payload["current_step"], "spoof", 0)

    embedding = faces[0]["embedding"]
    next_step, completed_steps, completed = next_step_for(payload["current_step"])
    warning = MESSAGES["transparent_specs"] if payload["has_specs"] and payload["current_step"] != "with_specs" else None
    db.add(FaceEmbedding(
        person_id=person.id,
        embedding_vector=json.dumps(embedding),
        pose_type=payload["current_step"],
        model_name=model_label(),
        quality_score=quality["quality_score"],
        brightness_score=quality["brightness_score"],
        blur_score=quality["blur_score"],
        face_angle=faces[0]["turn"],
        has_specs=payload["has_specs"],
        is_active=True,
    ))
    enrollment = db.query(FaceEnrollment).filter(FaceEnrollment.person_id == person.id).order_by(FaceEnrollment.id.desc()).first()
    if enrollment:
        enrollment.current_step = next_step
        enrollment.completed_steps = completed_steps
        enrollment.quality_score = quality["quality_score"]
        enrollment.has_specs_reference = enrollment.has_specs_reference or payload["current_step"] == "with_specs"
        if completed:
            enrollment.enrollment_status = "completed"
            enrollment.completed_at = datetime.utcnow()
            person.face_enrollment_status = "completed"
    db.commit()
    gallery_cache.clear()
    print("embedding saved or not", "saved")
    print("next_step", next_step)
    return {
        "success": True,
        "accepted": True,
        "message": f"{payload['current_step'].replace('_', ' ').title()} face captured successfully",
        "current_step": payload["current_step"],
        "next_step": next_step,
        "instruction": INSTRUCTIONS[next_step],
        "quality_status": "good",
        "progress_percentage": int((completed_steps / 5) * 100),
        "warning": warning,
        "completed": completed,
    }


def reject(message, current_step, quality_status, progress):
    return {
        "success": False,
        "accepted": False,
        "message": message,
        "current_step": current_step,
        "next_step": current_step,
        "instruction": INSTRUCTIONS.get(current_step, "Look straight"),
        "quality_status": quality_status,
        "progress_percentage": progress,
        "warning": message,
        "completed": False,
    }


@router.post("/enrollment/complete/{person_id}")
def complete_enrollment(person_id: int, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    person.face_enrollment_status = "completed"
    enrollment = db.query(FaceEnrollment).filter(FaceEnrollment.person_id == person_id).order_by(FaceEnrollment.id.desc()).first()
    if enrollment:
        enrollment.enrollment_status = "completed"
        enrollment.completed_steps = 5
        enrollment.completed_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": "Face enrollment completed", "data": {"person_id": person_id}}


@router.get("/enrollment/status/{person_id}")
def enrollment_status(person_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(FaceEnrollment).filter(FaceEnrollment.person_id == person_id).order_by(FaceEnrollment.id.desc()).first()
    return {"success": True, "message": "Enrollment status fetched", "data": face_enrollment_data(enrollment)}


def load_session(db, session_id):
    # Checked every few seconds rather than every frame; a stopped session is noticed within that time.
    cached = session_cache.get(session_id)
    if cached and time.monotonic() - cached[0] < SESSION_TTL_SECONDS:
        return cached[1]
    row = db.get(AttendanceSession, session_id)
    session = SimpleNamespace(id=row.id, course_id=row.course_id, batch_id=row.batch_id, status=row.status) if row else None
    session_cache[session_id] = (time.monotonic(), session)
    return session


def load_gallery(db, course_id, batch_id):
    # Live video asks for the same batch several times a second, and the stored vectors are a
    # large download from a remote database, so they are kept in memory for a short while.
    key = (course_id, batch_id, model_label())
    cached = gallery_cache.get(key)
    if cached and time.monotonic() - cached[0] < GALLERY_TTL_SECONDS:
        return cached[1]
    query = db.query(
        FaceEmbedding.person_id, FaceEmbedding.embedding_vector,
        Person.person_code, Person.full_name, Person.person_type,
    ).join(Person, FaceEmbedding.person_id == Person.id).filter(
        FaceEmbedding.is_active == True,
        FaceEmbedding.model_name == model_label(),
    )
    if course_id:
        query = query.filter(Person.course_id == course_id)
    if batch_id:
        query = query.filter(Person.batch_id == batch_id)
    gallery = build_gallery(query.all())
    gallery_cache[key] = (time.monotonic(), gallery)
    return gallery


def marked_status(db, session, person_id):
    # The same face shows up in many consecutive frames, so only the first one writes a record.
    key = (session.id, person_id, today_local())
    if key not in marked_today:
        existing = find_today_record(db, person_id, session.id)
        if existing:
            marked_today[key] = existing.status
    return marked_today.get(key)


def mark_for_session(db, session, person_id, confidence, device_name, live):
    if not confirm_match(session.id, person_id, live):
        return {"attendance_status": None, "newly_marked": False, "confirming": live}
    key = (session.id, person_id, today_local())
    record, message = mark_attendance(db, AttendanceMark(
        session_id=session.id,
        person_id=person_id,
        confidence_score=confidence,
        recognition_method="face_ai",
        device_name=device_name,
    ))
    if not record:
        return {"attendance_status": None, "newly_marked": False, "message": message}
    marked_today[key] = record.status
    return {"attendance_status": record.status, "newly_marked": True, "record": attendance_record_data(record)}


@router.post("/recognize")
async def recognize(request: Request, db: Session = Depends(get_db)):
    payload = await read_face_payload(request)
    image = payload["image"]
    if image is None:
        return {"success": False, "message": "Invalid image", "details": {}}
    try:
        # The models are slow enough to stall every other request if they ran on the event loop.
        faces = await run_in_threadpool(detect_faces, image)
    except RuntimeError as exc:
        return {"success": False, "recognized": False, "status": "embedding_failed", "message": str(exc)}

    height, width = image.shape[:2]
    frame = {"width": int(width), "height": int(height)}
    if not faces:
        return {"success": True, "recognized": False, "status": "no_face", "message": MESSAGES["no_face"], "frame": frame, "faces": []}

    session = load_session(db, payload["session_id"]) if payload["session_id"] else None
    course_id = session.course_id if session else payload["course_id"]
    batch_id = session.batch_id if session else payload["batch_id"]
    gallery = load_gallery(db, course_id, batch_id)

    results = []
    matches = []
    for face in faces:
        x, y, w, h = face["box"]
        item = {"box": {"x": x, "y": y, "w": w, "h": h}, "recognized": False, "status": "unknown", "message": "Unknown face"}
        results.append(item)
        if min(w, h) < MIN_FACE_SIZE:
            item.update(status="too_far", message=MESSAGES["too_far"])
            continue
        match = best_match(face["embedding"], gallery)
        if match:
            matches.append((match["confidence"], item, match["embedding"]))

    # One person cannot be two faces in the same frame: the strongest match keeps the name.
    active = bool(session and session.status == "active")
    seen = set()
    pending = []
    for confidence, item, person in sorted(matches, key=lambda entry: entry[0], reverse=True):
        if person.person_id in seen:
            continue
        seen.add(person.person_id)
        item.update(
            recognized=True,
            status="matched",
            person_id=person.person_id,
            person_code=person.person_code,
            person_name=person.full_name,
            person_type=person.person_type,
            confidence_score=round(confidence, 4),
            message=f"{person.full_name} recognized",
        )
        already = marked_status(db, session, person.person_id) if active else None
        if already:
            item.update(attendance_status=already, newly_marked=False)
        else:
            pending.append(item)

    # Liveness only runs for people who are not marked yet, which keeps a full classroom fast.
    if pending:
        boxes = [(item["box"]["x"], item["box"]["y"], item["box"]["w"], item["box"]["h"]) for item in pending]
        try:
            live = await run_in_threadpool(check_liveness, image, boxes)
        except RuntimeError as exc:
            return {"success": False, "recognized": False, "status": "embedding_failed", "message": str(exc)}
        for item, is_live in zip(pending, live):
            if active:
                item.update(mark_for_session(db, session, item["person_id"], item["confidence_score"], payload["device_name"], is_live))
            if not is_live:
                item.update(recognized=False, status="spoof", message=MESSAGES["spoof"])

    best = max((item for item in results if item["recognized"]), key=lambda item: item["confidence_score"], default=None)
    response = {
        "success": True,
        "recognized": bool(best),
        "status": "matched" if best else "unknown",
        "message": best["message"] if best else "Unknown face",
        "frame": frame,
        "faces": results,
    }
    if best:
        response.update({key: best[key] for key in ("person_id", "person_code", "person_name", "person_type", "confidence_score")})
    return response
