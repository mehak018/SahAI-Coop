from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database.base import Base


class SampleResponse(Base):
    """
    SQLAlchemy Model representing predefined verified legal/cooperative responses.
    Mapped to `sample_responses` table in MySQL.
    Acts as the baseline fallback knowledge base and pre-RAG response provider.
    """
    __tablename__ = "sample_responses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_keyword = Column(String(100), nullable=False, index=True)
    question_pattern = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    language = Column(String(10), nullable=False, default="en", index=True)
    source_title = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<SampleResponse(id={self.id}, topic='{self.topic_keyword}', lang='{self.language}')>"
