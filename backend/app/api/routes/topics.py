from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.topic_service import TopicService
from app.schemas.topic import TopicCategoryResponse, SampleQuestionResponse

router = APIRouter(tags=["Topics & Metadata"])


@router.get(
    "/topics",
    response_model=List[TopicCategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Fetch available topic categories",
    description=(
        "Retrieves the list of supported governance and legal topic categories "
        "(Crop Insurance, PACS Services, Grievances, etc.) to populate UI dashboard cards."
    )
)
def get_topics():
    """Returns available categories for the frontend cards."""
    return TopicService.get_topics()


@router.get(
    "/sample-questions",
    response_model=List[SampleQuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="Fetch popular suggested questions",
    description="Returns popular suggested quick questions to populate the 'Try asking:' pills in the chat UI."
)
def get_sample_questions(
    topic_category: Optional[str] = Query(None, description="Optional filter by topic category name"),
    language: Optional[str] = Query("en", description="Language code: 'en', 'hi', or 'mr'"),
    db: Session = Depends(get_db)
):
    """
    Returns suggested prompt questions:
    - **topic_category**: Filter by category (optional)
    - **language**: 'en', 'hi', or 'mr' (default: 'en')
    """
    return TopicService.get_sample_questions(
        db=db,
        topic_category=topic_category,
        language=language or "en"
    )
