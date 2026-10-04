import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./vernex_attendance.db")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    face_detector: str = os.getenv("FACE_DETECTOR", "yolov8n")
    face_model: str = os.getenv("FACE_MODEL", "Facenet512")
    # Pixel scaling applied before the model. Facenet2018 is what Facenet512 was trained with.
    face_normalization: str = os.getenv("FACE_NORMALIZATION", "Facenet2018")
    face_detection_confidence: float = float(os.getenv("FACE_DETECTION_CONFIDENCE", "0.50"))
    # Cosine similarity needed to accept a match, and how far the best person must lead the runner-up.
    face_match_threshold: float = float(os.getenv("FACE_MATCH_THRESHOLD", "0.60"))
    face_match_margin: float = float(os.getenv("FACE_MATCH_MARGIN", "0.05"))
    # Frames in which a person must be matched before attendance is written.
    face_confirm_frames: int = int(os.getenv("FACE_CONFIRM_FRAMES", "3"))
    # Reject photos and screens held up to the camera. The score is the model's "real face" probability.
    face_liveness: bool = os.getenv("FACE_LIVENESS", "true").lower() == "true"
    face_liveness_threshold: float = float(os.getenv("FACE_LIVENESS_THRESHOLD", "0.50"))
    google_script_url: str = os.getenv("GOOGLE_SCRIPT_URL", "")
    default_timezone: str = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")


settings = Settings()
