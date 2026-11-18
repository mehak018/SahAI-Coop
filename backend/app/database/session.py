import ssl
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

# Auto-normalize mysql:// to mysql+pymysql:// if dialect is omitted
db_url = settings.DATABASE_URL
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # If connecting to remote cloud database (TiDB, Aiven, AWS RDS) or ssl is specified
    db_url_lower = db_url.lower()
    if any(k in db_url_lower for k in ["tidbcloud", "aivencloud", "amazonaws", "ssl"]):
        connect_args["ssl"] = ssl.create_default_context()

    engine_kwargs.update({
        "pool_recycle": 3600,
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_engine(
    db_url,
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
