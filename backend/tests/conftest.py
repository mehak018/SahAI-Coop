import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Put backend folder in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database.base import Base
from app.api.deps import get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.sample_response import SampleResponse
from app.main import app

# In-memory SQLite engine for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def clean_db():
    """Drop and recreate all tables for each test to ensure complete isolation."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(clean_db):
    """Provides a fresh transactional test session with sample responses seeded."""
    session = TestingSessionLocal()

    # Seed knowledge base responses for testing
    sample_data = [
        SampleResponse(
            topic_keyword="Crop Insurance",
            question_pattern="crop insurance apply pmfby claim premium loss damaged",
            answer_text="You can enrol in PMFBY through your bank/PACS, a Common Service Centre, or the pmfby.gov.in portal.",
            language="en",
            source_title="PMFBY Official Portal",
            source_url="https://pmfby.gov.in"
        ),
        SampleResponse(
            topic_keyword="PACS Services",
            question_pattern="pacs services loan fertilizer seeds credit primary agricultural cooperative society",
            answer_text="Primary Agricultural Credit Societies (PACS) provide short-term crop loans and subsidized fertilizers.",
            language="en",
            source_title="Ministry of Cooperation",
            source_url="https://cooperation.gov.in"
        )
    ]
    for item in sample_data:
        session.add(item)
    session.commit()

    yield session

    session.close()


@pytest.fixture
def client(db_session):
    """Provides a TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
