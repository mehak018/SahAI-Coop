from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.topic import TopicCategoryResponse, SampleQuestionResponse


class TopicService:
    """Service providing topics, metadata, and suggested prompt questions."""

    # Static metadata definitions matching the Sahakar Saathi UI design
    STATIC_TOPICS = [
        {
            "id": "crop-insurance",
            "title": "Crop Insurance (PMFBY)",
            "slug": "crop-insurance",
            "icon": "🌾",
            "description": "Enrollment, claim filing within 72 hours, premium rates, and loss compensation guidelines.",
            "sample_queries": [
                "How do I apply for crop insurance?",
                "What is the premium rate for Kharif crops?",
                "How to report crop damage within 72 hours?"
            ]
        },
        {
            "id": "required-documents",
            "title": "Required Documents",
            "slug": "required-documents",
            "icon": "📄",
            "description": "7/12 extract, 8A, Aadhaar, crop declaration, and bank passbook requirements for schemes.",
            "sample_queries": [
                "What documents are required for KCC?",
                "Which land records are needed for PACS loan?",
                "Do I need a sowing certificate?"
            ]
        },
        {
            "id": "pacs-services",
            "title": "PACS Services",
            "slug": "pacs-services",
            "icon": "🏛️",
            "description": "Subsidized fertilizers, short-term crop credit, modern warehousing, and CSC services.",
            "sample_queries": [
                "What is PACS?",
                "How do I get subsidized fertilizer from PACS?",
                "Can I access banking services at computerized PACS?"
            ]
        },
        {
            "id": "grievance-assistance",
            "title": "Grievance Assistance",
            "slug": "grievance-assistance",
            "icon": "📢",
            "description": "Dispute resolution, complaint escalation against cooperative societies, and CPGRAMS filing.",
            "sample_queries": [
                "Where can I complain about a cooperative society?",
                "How to file a complaint against PACS management?",
                "What is the role of District Registrar in disputes?"
            ]
        },
        {
            "id": "cooperative-rules",
            "title": "Cooperative Society Rules",
            "slug": "cooperative-society-rules",
            "icon": "⚖️",
            "description": "Democratic member rights ('one member, one vote'), bylaws inspection, AGM, and audit rules.",
            "sample_queries": [
                "What are my voting rights in a cooperative society?",
                "Can a member inspect society audit reports?",
                "How often must an Annual General Meeting (AGM) be held?"
            ]
        },
        {
            "id": "government-schemes",
            "title": "Government Schemes",
            "slug": "government-schemes",
            "icon": "🏛️",
            "description": "PM-KISAN income support, Agriculture Infrastructure Fund (AIF), and NCDC assistance.",
            "sample_queries": [
                "What is the subsidy under Agriculture Infrastructure Fund?",
                "How do I check PM-KISAN installment status?",
                "What are NCDC schemes for dairy cooperatives?"
            ]
        }
    ]

    @classmethod
    def get_topics(cls) -> List[TopicCategoryResponse]:
        """Returns the full list of topic categories to render UI cards."""
        return [TopicCategoryResponse(**topic) for topic in cls.STATIC_TOPICS]

    @classmethod
    def get_sample_questions(
        cls, 
        db: Session, 
        topic_category: Optional[str] = None, 
        language: str = "en"
    ) -> List[SampleQuestionResponse]:
        """
        Retrieves popular suggested questions to populate the 'Try asking:' pills in the chat UI.
        Draws from predefined sample questions and database patterns.
        """
        questions = []
        
        # Multilingual quick question templates
        quick_questions_by_lang = {
            "en": [
                ("How do I apply for crop insurance?", "Crop Insurance"),
                ("What documents are required?", "Required Documents"),
                ("What is PACS?", "PACS Services"),
                ("Where can I complain about a cooperative society?", "Grievance Assistance"),
                ("What are my rights in a cooperative society?", "Cooperative Society Rules"),
                ("What subsidies are available for farmers?", "Government Schemes")
            ],
            "hi": [
                ("फसल बीमा योजना के लिए कैसे आवेदन करें?", "Crop Insurance"),
                ("ऋण और बीमा के लिए कौन से दस्तावेज चाहिए?", "Required Documents"),
                ("पैक्स (PACS) क्या है और इससे क्या लाभ हैं?", "PACS Services"),
                ("सहकारी समिति के खिलाफ शिकायत कहां दर्ज करें?", "Grievance Assistance"),
                ("सहकारी समिति में सदस्य के क्या कानूनी अधिकार हैं?", "Cooperative Society Rules"),
                ("किसानों के लिए कौन सी प्रमुख सरकारी योजनाएं हैं?", "Government Schemes")
            ],
            "mr": [
                ("पीक विम्यासाठी अर्ज कसा करावा?", "Crop Insurance"),
                ("सहकारी कर्जासाठी कोणती कागदपत्रे लागतात?", "Required Documents"),
                ("पॅक्स (PACS) म्हणजे काय?", "PACS Services"),
                ("सहकारी संस्थेविरुद्ध तक्रार कुठे करावी?", "Grievance Assistance"),
                ("सहकारी संस्थेत सभासदांचे काय अधिकार आहेत?", "Cooperative Society Rules"),
                ("शेतकऱ्यांसाठी शासकीय अनुदान योजना कोणत्या आहेत?", "Government Schemes")
            ]
        }

        lang_key = language if language in quick_questions_by_lang else "en"
        items = quick_questions_by_lang[lang_key]

        qid = 1
        for q_text, t_cat in items:
            if topic_category and topic_category.lower() not in t_cat.lower():
                continue
            questions.append(
                SampleQuestionResponse(
                    id=qid,
                    question=q_text,
                    topic_category=t_cat,
                    language=lang_key
                )
            )
            qid += 1

        return questions
