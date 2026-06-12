import json
import math

import numpy as np

from app.config import settings

try:
    from deepface import DeepFace
except Exception:
    DeepFace = None

ENROLLMENT_STEPS = ["front", "left", "right", "close", "far", "with_specs"]


def generate_embedding(image):
    # DeepFace creates the MVP face embedding. We do not train any model here.
    if DeepFace is None:
        raise RuntimeError("DeepFace is not installed or failed to import. Install requirements and retry.")
    try:
        rgb = image[:, :, ::-1]
        reps = DeepFace.represent(rgb, model_name="Facenet", enforce_detection=False)
        if not reps:
            raise RuntimeError("DeepFace did not return an embedding.")
        return reps[0]["embedding"]
    except Exception as exc:
        raise RuntimeError(f"Embedding generation failed: {exc}") from exc


def cosine_similarity(a, b):
    av = np.array(a, dtype=float)
    bv = np.array(b, dtype=float)
    denom = np.linalg.norm(av) * np.linalg.norm(bv)
    if denom == 0:
        return 0.0
    return float(np.dot(av, bv) / denom)


def best_match(live_embedding, embeddings):
    best = None
    for item in embeddings:
        stored = json.loads(item.embedding_vector)
        score = cosine_similarity(live_embedding, stored)
        if best is None or score > best["confidence"]:
            best = {"embedding": item, "confidence": score}
    if best and best["confidence"] >= settings.face_match_threshold:
        return best
    return None


def next_step_for(current_step):
    if current_step not in ENROLLMENT_STEPS:
        return "front", 0, False
    index = ENROLLMENT_STEPS.index(current_step)
    base_total = 5
    completed = min(index + 1, base_total)
    completed_flag = index >= base_total - 1 and current_step != "with_specs"
    next_step = ENROLLMENT_STEPS[index + 1] if index + 1 < base_total else None
    return next_step, completed, completed_flag
