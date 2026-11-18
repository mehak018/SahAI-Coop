from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Engine configuration tailored for MySQL connection pooling
# pool_pre_ping checks connectivity before checkout, avoiding stale MySQL connection drops
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    engine_kwargs.update({
        "pool_recycle": 3600,
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures it closes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
