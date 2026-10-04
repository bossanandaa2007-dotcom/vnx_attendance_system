import json
import time

import numpy as np

from app.config import settings

DeepFace = None
DeepFaceImportError = None
liveness_models = None


def get_deepface():
    global DeepFace, DeepFaceImportError
    if DeepFace is not None:
        return DeepFace
    if DeepFaceImportError is not None:
        raise RuntimeError(f"DeepFace failed to import: {DeepFaceImportError}")
    try:
        from deepface import DeepFace as ImportedDeepFace
    except Exception as exc:
        DeepFaceImportError = exc
        raise RuntimeError(f"DeepFace failed to import: {exc}") from exc
    DeepFace = ImportedDeepFace
    try:
        compile_recognition_model()
    except Exception as exc:
        print("recognition model runs uncompiled (slower):", exc)
    return DeepFace


def compile_recognition_model():
    # DeepFace calls the Keras model eagerly, layer by layer. Running it as one compiled graph
    # returns the same vectors several times faster, which is what keeps live video smooth.
    import tensorflow as tf
    from deepface.modules import modeling

    client = modeling.build_model(task="facial_recognition", model_name=settings.face_model)
    if not hasattr(client.model, "predict_on_batch"):
        return
    height, width = client.input_shape
    graph = tf.function(
        lambda batch: client.model(batch, training=False),
        input_signature=[tf.TensorSpec([None, height, width, 3], tf.float32)],
    )

    def forward(img):
        if img.ndim == 3:
            img = np.expand_dims(img, axis=0)
        embeddings = graph(tf.constant(img, dtype=tf.float32)).numpy()
        return embeddings[0].tolist() if embeddings.shape[0] == 1 else embeddings.tolist()

    client.forward = forward


def get_liveness_models():
    global liveness_models
    if liveness_models is None:
        import tensorflow as tf
        from deepface.modules import modeling

        get_deepface()
        fasnet = modeling.build_model(task="spoofing", model_name="Fasnet")
        signature = [tf.TensorSpec([None, 80, 80, 3], tf.float32)]
        liveness_models = [
            (tf.function(lambda batch, model=model: model(batch, training=False), input_signature=signature), scale)
            for model, scale in ((fasnet.first_model, 2.7), (fasnet.second_model, 4))
        ]
    return liveness_models


def check_liveness(image, boxes):
    # MiniFASNet looks at each face together with its surroundings: a printed photo or a phone
    # screen shows edges, glare and flat texture that a real face in a room does not.
    # Returns one True (live) / False (photo or screen) per box.
    if not settings.face_liveness or not boxes:
        return [True] * len(boxes)
    try:
        import tensorflow as tf
        from deepface.models.spoofing.FasNetUtils import crop

        votes = np.zeros((len(boxes), 3))
        for model, scale in get_liveness_models():
            crops = np.stack([crop(image, tuple(box), scale, 80, 80) for box in boxes]).astype(np.float32)
            logits = model(tf.constant(crops)).numpy()
            exps = np.exp(logits - logits.max(axis=1, keepdims=True))
            votes += exps / exps.sum(axis=1, keepdims=True)
    except Exception as exc:
        raise RuntimeError(f"Liveness check failed: {exc}") from exc
    # Column 1 is the "real face" class; the two models' votes are averaged.
    return [bool(score >= settings.face_liveness_threshold) for score in votes[:, 1] / 2]


ENROLLMENT_STEPS = ["front", "left", "right", "close", "far", "with_specs"]


def model_label():
    # Stored with every embedding. Vectors from different models are not comparable.
    return f"DeepFace-{settings.face_model}-{settings.face_normalization}"


def detect_faces(image):
    # YOLO finds every face in the frame, then the embedding model encodes each one.
    # Both are pretrained. We do not train any model here.
    deepface = get_deepface()
    try:
        reps = deepface.represent(
            image,
            model_name=settings.face_model,
            detector_backend=settings.face_detector,
            enforce_detection=False,
            align=True,
            normalization=settings.face_normalization,
        )
    except Exception as exc:
        raise RuntimeError(f"Face detection failed: {exc}") from exc

    faces = []
    for rep in reps:
        # With enforce_detection=False a frame without faces comes back as one
        # zero-confidence "face" covering the whole image, so drop weak detections.
        confidence = float(rep.get("face_confidence") or 0)
        if confidence < settings.face_detection_confidence:
            continue
        area = rep["facial_area"]
        faces.append({
            "box": [int(area["x"]), int(area["y"]), int(area["w"]), int(area["h"])],
            "embedding": rep["embedding"],
            "detection_confidence": confidence,
            "turn": head_turn(area),
        })
    return faces


def head_turn(area):
    # When the head turns, the eyes slide sideways inside the face box. The value is that shift as a
    # share of the box width: about 0 looking straight, positive when turned to the person's own left.
    left_eye, right_eye = area.get("left_eye"), area.get("right_eye")
    if not left_eye or not right_eye or not area["w"]:
        return None
    eyes_x = (left_eye[0] + right_eye[0]) / 2
    return float((eyes_x - (area["x"] + area["w"] / 2)) / area["w"])


def warm_up():
    # Loading the models takes around half a minute, so do it at startup instead of on the first scan.
    try:
        blank = np.zeros((160, 160, 3), dtype=np.uint8)
        detect_faces(blank)
        check_liveness(blank, [(40, 40, 80, 80)])
        print("face models ready")
    except Exception as exc:
        print("face models failed to load:", exc)


def build_gallery(embeddings):
    # Parse stored vectors once per frame so every detected face reuses them.
    embeddings = list(embeddings)
    if not embeddings:
        return embeddings, None
    matrix = np.array([json.loads(item.embedding_vector) for item in embeddings], dtype=float)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return embeddings, matrix / norms


def best_match(live_embedding, gallery):
    items, matrix = gallery
    if matrix is None:
        return None
    live = np.array(live_embedding, dtype=float)
    norm = np.linalg.norm(live)
    if norm == 0:
        return None
    scores = matrix @ (live / norm)
    index = int(np.argmax(scores))
    if scores[index] < settings.face_match_threshold:
        return None
    # A face that looks almost as much like a second person is ambiguous, so it stays unknown.
    person_id = items[index].person_id
    others = [score for item, score in zip(items, scores) if item.person_id != person_id]
    if others and scores[index] - max(others) < settings.face_match_margin:
        return None
    return {"embedding": items[index], "confidence": float(scores[index])}


CONFIRM_WINDOW_SECONDS = 10
SPOOF_COOLDOWN_SECONDS = 3
recent_matches = {}
blocked_until = {}


def confirm_match(session_id, person_id, live=True):
    # One frame can be wrong, so a person only counts once matched in several recent frames.
    now = time.monotonic()
    key = (session_id, person_id)
    if not live:
        # A photo must not collect hits a lucky frame at a time: a spoof verdict wipes them
        # and pauses counting, so every frame of the run has to look live.
        recent_matches[key] = []
        blocked_until[key] = now + SPOOF_COOLDOWN_SECONDS
        return False
    if now < blocked_until.get(key, 0):
        return False
    hits = [seen for seen in recent_matches.get(key, []) if now - seen <= CONFIRM_WINDOW_SECONDS]
    hits.append(now)
    recent_matches[key] = hits
    return len(hits) >= settings.face_confirm_frames


def next_step_for(current_step):
    if current_step not in ENROLLMENT_STEPS:
        return "front", 0, False
    index = ENROLLMENT_STEPS.index(current_step)
    base_total = 5
    completed = min(index + 1, base_total)
    completed_flag = index >= base_total - 1 and current_step != "with_specs"
    next_step = ENROLLMENT_STEPS[index + 1] if index + 1 < base_total else None
    return next_step, completed, completed_flag
