from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.base import Base


class Message(Base):
    """
    SQLAlchemy Model representing conversational messages (from user and bot).
    Mapped to `messages` table in MySQL.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(
        Integer, 
        ForeignKey("chat_sessions.id", ondelete="CASCADE", onupdate="CASCADE"), 
        nullable=False, 
        index=True
    )
    sender = Column(String(20), nullable=False)  # 'user' or 'bot'
    content = Column(Text, nullable=False)
    language = Column(String(10), nullable=False, default="en")
    topic_category = Column(String(100), nullable=True, index=True)
    source_reference = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # N:1 Relationship with ChatSession
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, session_id={self.session_id}, sender='{self.sender}', topic='{self.topic_category}')>"
