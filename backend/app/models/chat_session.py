from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.base import Base


class ChatSession(Base):
    """
    SQLAlchemy Model representing conversational chat sessions for users.
    Mapped to `chat_sessions` table in MySQL.
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), 
        nullable=False, 
        index=True
    )
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # N:1 Relationship with User
    user = relationship("User", back_populates="sessions")

    # 1:N Relationship with Message
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Message.timestamp.asc()"
    )

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
