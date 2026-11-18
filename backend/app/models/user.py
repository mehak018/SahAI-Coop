from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database.base import Base


class User(Base):
    """
    SQLAlchemy Model representing system users (citizens, farmers, cooperative members).
    Mapped to `users` table in MySQL.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    preferred_language = Column(String(10), nullable=False, default="en", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 1:N Relationship with ChatSession
    sessions = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', language='{self.preferred_language}')>"
