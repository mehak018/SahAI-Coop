from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.chat_session import ChatSession
from app.models.message import Message


class ChatRepository:
    """Repository handling all CRUD database operations for Chat Sessions and Messages."""

    @staticmethod
    def create_session(db: Session, user_id: int, title: Optional[str] = None) -> ChatSession:
        default_title = title.strip() if title and title.strip() else "New Conversation"
        session = ChatSession(
            user_id=user_id,
            title=default_title
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_by_id(db: Session, session_id: int) -> Optional[ChatSession]:
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()

    @staticmethod
    def get_sessions_by_user_id(db: Session, user_id: int) -> List[ChatSession]:
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    @staticmethod
    def update_session_title(db: Session, session_id: int, new_title: str) -> Optional[ChatSession]:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.title = new_title[:255]
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def create_message(
        db: Session,
        session_id: int,
        sender: str,
        content: str,
        language: str = "en",
        topic_category: Optional[str] = None,
        source_reference: Optional[str] = None
    ) -> Message:
        message = Message(
            session_id=session_id,
            sender=sender,
            content=content,
            language=language,
            topic_category=topic_category,
            source_reference=source_reference
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_messages_by_session_id(db: Session, session_id: int) -> List[Message]:
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.timestamp.asc(), Message.id.asc())
            .all()
        )

    @staticmethod
    def count_messages_in_session(db: Session, session_id: int) -> int:
        return db.query(func.count(Message.id)).filter(Message.session_id == session_id).scalar() or 0
