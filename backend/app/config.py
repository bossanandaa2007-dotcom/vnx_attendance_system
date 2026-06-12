import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./vernex_attendance.db")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    face_match_threshold: float = float(os.getenv("FACE_MATCH_THRESHOLD", "0.60"))
    google_script_url: str = os.getenv("GOOGLE_SCRIPT_URL", "")
    default_timezone: str = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")


settings = Settings()
