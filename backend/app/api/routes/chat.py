from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    MessageCreate,
    ChatInteractionResponse,
    ChatHistoryResponse
)

router = APIRouter(prefix="/chat", tags=["Chat & Messaging"])


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session",
    description="Initializes a new conversational session for the designated user."
)
def create_session(
    request: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new chat session:
    - **user_id**: ID of the registered user
    - **title**: Optional conversation title
    """
    return ChatService.create_session(
        db=db,
        user_id=request.user_id,
        title=request.title
    )


@router.get(
    "/sessions/{user_id}",
    response_model=List[ChatSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all chat sessions for a user",
    description="Returns all previous chat sessions belonging to a user, ordered newest first."
)
def get_user_sessions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Fetches chat sessions for a specific user:
    - **user_id**: Target user ID
    """
    return ChatService.get_user_sessions(db=db, user_id=user_id)


@router.post(
    "/message",
    response_model=ChatInteractionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send user message and receive AI / Knowledge bot response",
    description=(
        "Saves the user message, attempts AI/RAG or matches against verified sample responses "
        "in MySQL, saves the bot reply, and returns both messages with verified sources/citations."
    )
)
async def send_message(
    request: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Sends a query into a session:
    - **session_id**: Active session ID
    - **content**: Question text in English, Hindi, or Marathi
    - **language**: 'en', 'hi', or 'mr'
    """
    return await ChatService.process_user_message(
        db=db,
        session_id=request.session_id,
        content=request.content,
        language=request.language or "en"
    )


@router.get(
    "/history/{session_id}",
    response_model=ChatHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve message history for a session",
    description="Returns the full chronological message log for a specific chat session."
)
def get_session_history(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Gets conversation history:
    - **session_id**: Target session ID
    """
    return ChatService.get_session_history(db=db, session_id=session_id)
