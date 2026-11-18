from typing import Optional, List
from pydantic import BaseModel, Field


class TopicCategoryResponse(BaseModel):
    """Schema for returning topic categories for the UI dashboard cards."""
    id: str
    title: str
    slug: str
    icon: str
    description: str
    sample_queries: List[str] = Field(default_factory=list)


class SampleQuestionResponse(BaseModel):
    """Schema for returning suggested quick-ask questions."""
    id: int
    question: str
    topic_category: str
    language: str
