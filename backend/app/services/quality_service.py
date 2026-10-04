import cv2

MESSAGES = {
    "no_face": "No face detected. Please keep your face inside the circle.",
    "multiple": "Multiple faces detected. Only one person is allowed.",
    "low_light": "Low light detected. Move to a brighter place.",
    "blurry": "Image is blurry. Keep your face still.",
    "too_far": "Face too far. Move closer.",
    "too_close": "Face too close. Move backward.",
    "not_centered": "Keep your face centered inside the circle.",
    "sunglasses": "Please remove sunglasses.",
    "spoof": "Photo or screen detected. Show your real face to the camera.",
    "transparent_specs": "Transparent spectacles detected. You can continue, but removing specs improves enrollment accuracy.",
}


# Eye shift inside the face box (share of its width) that counts as a real head turn, roughly 15 degrees.
MIN_HEAD_TURN = 0.06


def check_quality(image, faces, reject_sunglasses=True):
    # faces: [x, y, w, h] boxes from the YOLO detector (face_service.detect_faces).
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("detected face count", len(faces))
    brightness = float(gray.mean())
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if len(faces) == 0:
        return result(False, "no_face", brightness, blur, faces)
    if len(faces) > 1:
        return result(False, "multiple", brightness, blur, faces)
    h, w = gray.shape
    x, y, fw, fh = faces[0]
    face_ratio = (fw * fh) / float(w * h)
    cx = x + fw / 2
    if brightness < 55:
        return result(False, "low_light", brightness, blur, faces)
    if blur < 45:
        return result(False, "blurry", brightness, blur, faces)
    if face_ratio < 0.06:
        return result(False, "too_far", brightness, blur, faces)
    if face_ratio > 0.70:
        return result(False, "too_close", brightness, blur, faces)
    if abs(cx - w / 2) > w * 0.28:
        return result(False, "not_centered", brightness, blur, faces)
    if reject_sunglasses and has_dark_eye_region(gray, faces[0]):
        return result(False, "sunglasses", brightness, blur, faces)
    return {
        "ok": True,
        "quality_status": "good",
        "warning": None,
        "quality_score": min(1.0, (brightness / 160 + blur / 300) / 2),
        "brightness_score": brightness,
        "blur_score": blur,
        "face_box": [int(v) for v in faces[0]],
        "face_ratio": face_ratio,
        "center_x_ratio": cx / w,
    }


def check_pose(image, quality, step, turn=None):
    # turn: face_service.head_turn, positive when the head is turned to the person's own left.
    ratio = quality["face_ratio"]
    cx = quality["center_x_ratio"]
    if step == "front" and abs(cx - 0.5) > 0.18:
        return False, "Keep your face centered inside the circle."
    if turn is not None and step in ("left", "right"):
        wanted = turn if step == "left" else -turn
        if wanted <= -MIN_HEAD_TURN:
            return False, "Turn your head the other way."
        if wanted < MIN_HEAD_TURN:
            return False, f"Turn your head a little more to your {step}."
    if step == "close" and ratio < 0.22:
        return False, "Face too far. Move closer."
    if step == "far" and ratio > 0.24:
        return False, "Face too close. Move backward."
    return True, None


def has_dark_eye_region(gray, face):
    x, y, fw, fh = face
    eye_roi = gray[y + int(fh * 0.20): y + int(fh * 0.48), x + int(fw * 0.15): x + int(fw * 0.85)]
    return eye_roi.size > 0 and float(eye_roi.mean()) < 35


def result(ok, code, brightness, blur, faces):
    return {
        "ok": ok,
        "quality_status": code,
        "warning": MESSAGES[code],
        "quality_score": 0.0,
        "brightness_score": brightness,
        "blur_score": blur,
        "face_box": [int(v) for v in faces[0]] if len(faces) else None,
        "face_ratio": 0.0,
        "center_x_ratio": 0.0,
    }
