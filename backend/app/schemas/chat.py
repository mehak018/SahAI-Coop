from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    """Schema to create a new chat session."""
    user_id: int = Field(..., description="ID of the user initiating the session")
    title: Optional[str] = Field(
        default="New Conversation", 
        max_length=255, 
        description="Optional title for the conversation"
    )


class ChatSessionResponse(BaseModel):
    """Schema for chat session representation."""
    id: int
    user_id: int
    title: str
    created_at: datetime
    message_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    """Schema for sending a user message."""
    session_id: int = Field(..., description="ID of the active chat session")
    content: str = Field(..., min_length=1, description="Text question asked by the citizen/farmer")
    language: Optional[str] = Field(
        default="en", 
        pattern="^(en|hi|mr)$", 
        description="Language of the question: 'en', 'hi', or 'mr'"
    )


class MessageResponse(BaseModel):
    """Schema for a single message in the chat."""
    id: int
    session_id: int
    sender: str  # 'user' or 'bot'
    content: str
    language: str
    topic_category: Optional[str] = None
    source_reference: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class ChatInteractionResponse(BaseModel):
    """
    Schema returned after POST /api/chat/message.
    Contains both the persisted user question and the generated bot response.
    """
    user_message: MessageResponse
    bot_message: MessageResponse


class ChatHistoryResponse(BaseModel):
    """Schema for returning conversation history of a session."""
    session_id: int
    title: str
    messages: List[MessageResponse]
