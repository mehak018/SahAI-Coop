import re
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.sample_response import SampleResponse


class KnowledgeRepository:
    """Repository handling search and queries on sample_responses (Knowledge Base)."""

    @staticmethod
    def get_all(db: Session, language: Optional[str] = None) -> List[SampleResponse]:
        query = db.query(SampleResponse)
        if language:
            query = query.filter(SampleResponse.language == language)
        return query.all()

    @staticmethod
    def find_match(db: Session, user_query: str, language: str = "en") -> Optional[SampleResponse]:
        """
        Intelligent keyword & pattern matching against sample_responses.
        Matches question patterns and topic keywords with query tokens.
        First tries in the requested language, then falls back to English if unmatched.
        """
        cleaned_query = user_query.lower().strip()
        query_words = set(re.findall(r"\w+", cleaned_query))
        
        # English stop-words filter
        stop_words = {"what", "is", "are", "how", "do", "i", "can", "to", "for", "the", "a", "an", "in", "of", "on", "about", "me", "my", "you", "please"}
        content_words = {w for w in query_words if w not in stop_words and len(w) > 1}
        if not content_words:
            content_words = query_words

        # Candidate selection in requested language
        candidates = db.query(SampleResponse).filter(SampleResponse.language == language).all()
        if not candidates and language != "en":
            # Fallback to English candidates if language specific ones are absent
            candidates = db.query(SampleResponse).filter(SampleResponse.language == "en").all()

        best_candidate: Optional[SampleResponse] = None
        highest_score = 0

        for item in candidates:
            score = 0
            topic_lower = item.topic_keyword.lower()
            pattern_lower = item.question_pattern.lower()

            # Exact phrase match in topic or pattern
            if topic_lower in cleaned_query:
                score += 50
            if cleaned_query in pattern_lower:
                score += 50

            # Token overlap scoring
            pattern_words = set(re.findall(r"\w+", pattern_lower))
            topic_words = set(re.findall(r"\w+", topic_lower))
            
            matched_pattern_tokens = content_words.intersection(pattern_words)
            matched_topic_tokens = content_words.intersection(topic_words)
            
            score += len(matched_pattern_tokens) * 10
            score += len(matched_topic_tokens) * 20

            if score > highest_score:
                highest_score = score
                best_candidate = item

        # Return match if confidence score threshold met (at least 1 keyword match)
        if highest_score >= 10:
            return best_candidate

        return None
