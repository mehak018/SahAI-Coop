from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.rag_hook import AIRAGHook
from app.schemas.chat import (
    ChatSessionResponse,
    MessageResponse,
    ChatInteractionResponse,
    ChatHistoryResponse
)


class ChatService:
    """Service handling chat sessions, messaging lifecycle, and bot response synthesis."""

    # Fallback response messages when no direct match is found in the database
    FALLBACK_RESPONSES = {
        "en": (
            "I could not locate an exact match for your inquiry in our pre-indexed cooperative guidelines. "
            "For authoritative assistance, please consult the Ministry of Cooperation portal or visit your "
            "local Primary Agricultural Credit Society (PACS) office or District Cooperative Registrar."
        ),
        "hi": (
            "मुझे आपके प्रश्न के लिए हमारे सत्यापित सहकारिता नियमों में सटीक उत्तर नहीं मिला। "
            "आधिकारिक जानकारी और सहायता के लिए कृपया सहकारिता मंत्रालय पोर्टल पर जाएं अथवा अपने "
            "स्थानीय पैक्स (PACS) कार्यालय या जिला सहकारी निबंधक से संपर्क करें।"
        ),
        "mr": (
            "आपल्या विचारलेल्या प्रश्नासाठी थेट उत्तर उपलब्ध झाले नाही. "
            "अधिकृत मार्गदर्शनासाठी कृपया सहकार मंत्रालय पोर्टल तपासा अथवा आपल्या स्थानिक प्राथमिक कृषी "
            "पतसंस्था (PACS) किंवा जिल्हा उपनिबंधक कार्यालयाशी संपर्क साधावा."
        )
    }

    DEFAULT_SOURCES = {
        "en": "Ministry of Cooperation, Government of India (https://cooperation.gov.in)",
        "hi": "सहकारिता मंत्रालय, भारत सरकार (https://cooperation.gov.in)",
        "mr": "सहकार मंत्रालय, भारत सरकार (https://cooperation.gov.in)"
    }

    @classmethod
    def create_session(cls, db: Session, user_id: int, title: Optional[str] = None) -> ChatSessionResponse:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot create session: User with ID {user_id} does not exist."
            )

        session = ChatRepository.create_session(db, user_id=user_id, title=title)
        return ChatSessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            created_at=session.created_at,
            message_count=0
        )

    @classmethod
    def get_user_sessions(cls, db: Session, user_id: int) -> List[ChatSessionResponse]:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} does not exist."
            )

        sessions = ChatRepository.get_sessions_by_user_id(db, user_id)
        result = []
        for s in sessions:
            count = ChatRepository.count_messages_in_session(db, s.id)
            result.append(
                ChatSessionResponse(
                    id=s.id,
                    user_id=s.user_id,
                    title=s.title,
                    created_at=s.created_at,
                    message_count=count
                )
            )
        return result

    @classmethod
    def get_session_history(cls, db: Session, session_id: int) -> ChatHistoryResponse:
        session = ChatRepository.get_session_by_id(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session with ID {session_id} not found."
            )

        messages = ChatRepository.get_messages_by_session_id(db, session_id)
        message_responses = [MessageResponse.model_validate(m) for m in messages]

        return ChatHistoryResponse(
            session_id=session.id,
            title=session.title,
            messages=message_responses
        )

    @classmethod
    async def process_user_message(
        cls, 
        db: Session, 
        session_id: int, 
        content: str, 
        language: str = "en"
    ) -> ChatInteractionResponse:
        """
        Processes an incoming user message:
        1. Validates chat session existence.
        2. Persists the user message.
        3. Attempts AI/RAG engine query hook.
        4. If RAG is unavailable/unmatched, executes intelligent sample response matching in MySQL.
        5. Falls back to multilingual guidance if unmatched.
        6. Persists the bot response and updates session title if necessary.
        """
        session = ChatRepository.get_session_by_id(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat session with ID {session_id} not found."
            )

        # Normalize language
        lang = language.lower() if language in ("en", "hi", "mr") else "en"

        # Fetch recent conversation history (last 6 messages) before saving current turn
        prior_messages = ChatRepository.get_messages_by_session_id(db, session_id)
        recent_history = [
            {"sender": m.sender, "content": m.content}
            for m in prior_messages[-6:]
        ]

        # 1. Save user question
        user_msg = ChatRepository.create_message(
            db=db,
            session_id=session_id,
            sender="user",
            content=content.strip(),
            language=lang,
            topic_category=None,
            source_reference=None
        )

        # 2. Hook: Query external AI / RAG module if enabled
        rag_result = await AIRAGHook.query_rag_engine(
            query=content,
            language=lang,
            history=recent_history
        )
        
        bot_content = None
        topic_category = None
        source_reference = None

        if rag_result and rag_result.get("answer"):
            bot_content = rag_result["answer"]
            topic_category = rag_result.get("topic", "Cooperative AI")
            source_reference = rag_result.get("source_reference")
        else:
            # 3. Fallback: Intelligent Keyword Matching in MySQL sample_responses table
            matched_response = KnowledgeRepository.find_match(
                db=db, 
                user_query=content, 
                language=lang
            )

            if matched_response:
                bot_content = matched_response.answer_text
                topic_category = matched_response.topic_keyword
                source_reference = f"{matched_response.source_title} ({matched_response.source_url})"
            else:
                # 4. Courteous Default Multilingual Guidance
                bot_content = cls.FALLBACK_RESPONSES.get(lang, cls.FALLBACK_RESPONSES["en"])
                topic_category = "General Inquiry"
                source_reference = cls.DEFAULT_SOURCES.get(lang, cls.DEFAULT_SOURCES["en"])

        # 5. Save bot response
        bot_msg = ChatRepository.create_message(
            db=db,
            session_id=session_id,
            sender="bot",
            content=bot_content,
            language=lang,
            topic_category=topic_category,
            source_reference=source_reference
        )

        # 6. Auto-update session title if it's currently the default
        if session.title in ("New Conversation", "New Chat") and content.strip():
            # Create a concise title from the user query
            summary_title = content.strip()[:35]
            if len(content.strip()) > 35:
                summary_title += "..."
            ChatRepository.update_session_title(db, session_id, summary_title)

        return ChatInteractionResponse(
            user_message=MessageResponse.model_validate(user_msg),
            bot_message=MessageResponse.model_validate(bot_msg)
        )
