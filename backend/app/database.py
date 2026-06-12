from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


def clean_database_url(raw_url: str) -> str:
    url = (raw_url or "").strip().strip("\"'")
    if "pgbouncer=true" in url.lower():
        raise ValueError("Remove '?pgbouncer=true' from DATABASE_URL. Use the Supabase pooler host/port directly.")
    parsed = make_url(url)
    if parsed.host and "@" in parsed.host:
        raise ValueError("DATABASE_URL host contains '@'. Your password likely has an unencoded '@'. Encode '@' as '%40' and '%' as '%25'.")
    print("Database URL debug:", {
        "drivername": parsed.drivername,
        "username": parsed.username,
        "host": parsed.host,
        "port": parsed.port,
        "database": parsed.database,
        "password": "***" if parsed.password else None,
    })
    return url


DATABASE_URL = clean_database_url(settings.database_url)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
