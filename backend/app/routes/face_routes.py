import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.face_embedding import FaceEmbedding, FaceEnrollment
from app.models.person import Person
from app.services.face_service import best_match, generate_embedding, next_step_for
from app.services.quality_service import MESSAGES, check_pose, check_quality
from app.utils.image_utils import decode_base64_image, decode_image_bytes

router = APIRouter(prefix="/face", tags=["Face"])
INSTRUCTIONS = {
    "front": "Look straight",
    "left": "Move face slightly left",
    "right": "Move face slightly right",
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
            "device_name": form.get("device_name"),
            "image": image,
        }
    body = await request.json()
    return {
        "person_id": body.get("person_id"),
        "current_step": body.get("current_step", "front"),
        "has_specs": bool(body.get("has_specs", False)),
        "session_id": body.get("session_id"),
        "device_name": body.get("device_name"),
        "image": decode_base64_image(body.get("image_base64") or ""),
    }


@router.post("/enrollment/start/{person_id}")
def start_enrollment(person_id: int, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    print("start enrollment person_id", person_id)
    person.face_enrollment_status = "in_progress"
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
    return {"success": True, "message": "Face enrollment started", "data": enrollment}


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

    quality = check_quality(image, reject_sunglasses=True)
    print("quality result", quality)
    if not quality["ok"]:
        print("embedding saved or not", "not_saved")
        return reject(quality["warning"], payload["current_step"], quality["quality_status"], 0)

    pose_ok, pose_warning = check_pose(image, quality, payload["current_step"])
    print("pose result", {"ok": pose_ok, "warning": pose_warning})
    if not pose_ok:
        print("embedding saved or not", "not_saved")
        return reject(pose_warning, payload["current_step"], "bad", 0)

    try:
        embedding = generate_embedding(image)
    except RuntimeError as exc:
        print("embedding saved or not", "not_saved")
        return reject(str(exc), payload["current_step"], "embedding_failed", 0)

    next_step, completed_steps, completed = next_step_for(payload["current_step"])
    warning = MESSAGES["transparent_specs"] if payload["has_specs"] and payload["current_step"] != "with_specs" else None
    db.add(FaceEmbedding(
        person_id=person.id,
        embedding_vector=json.dumps(embedding),
        pose_type=payload["current_step"],
        model_name="DeepFace-Facenet",
        quality_score=quality["quality_score"],
        brightness_score=quality["brightness_score"],
        blur_score=quality["blur_score"],
        face_angle=None,
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
    return {"success": True, "message": "Enrollment status fetched", "data": enrollment}


@router.post("/recognize")
async def recognize(request: Request, db: Session = Depends(get_db)):
    payload = await read_face_payload(request)
    image = payload["image"]
    if image is None:
        return {"success": False, "message": "Invalid image", "details": {}}
    quality = check_quality(image, reject_sunglasses=False)
    if not quality["ok"]:
        return {"success": False, "recognized": False, "status": quality["quality_status"], "message": quality["warning"]}
    try:
        live_embedding = generate_embedding(image)
    except RuntimeError as exc:
        return {"success": False, "recognized": False, "status": "embedding_failed", "message": str(exc)}

    embeddings = db.query(FaceEmbedding).filter(FaceEmbedding.is_active == True).all()
    match = best_match(live_embedding, embeddings)
    if not match:
        return {"success": True, "recognized": False, "status": "unknown", "message": "Unknown face"}
    person = db.get(Person, match["embedding"].person_id)
    return {
        "success": True,
        "recognized": True,
        "person_id": person.id,
        "person_code": person.person_code,
        "person_name": person.full_name,
        "person_type": person.person_type,
        "confidence_score": round(match["confidence"], 4),
        "status": "matched",
        "message": f"{person.full_name} recognized",
    }
