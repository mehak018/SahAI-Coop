"""Multilingual language detection and Unicode tokenization utilities."""

import re
from typing import List

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "mr": "Marathi (मराठी)",
}

# Distinctive Marathi function words vs Hindi function words (Devanagari script)
MARATHI_CUES = {
    "आहे", "आहेत", "नाही", "करावे", "करावा", "कसे", "कसा", "कशी", "काय",
    "कुठे", "कोणत्या", "कोणती", "लागतात", "शेतकरी", "शेतकऱ्यांसाठी", "पीक",
    "विमा", "विम्यासाठी", "सातबारा", "कागदपत्रे", "संस्था", "संस्थेविरुद्ध",
    "सभासद", "तक्रार", "कर्ज", "कर्जासाठी", "माहिती", "हवी", "मला", "तुम्ही",
    "आपल्या", "मध्ये", "साठी", "द्वारे", "यांची", "मिळते", "पॅक्स",
}

HINDI_CUES = {
    "है", "हैं", "नहीं", "कैसे", "क्या", "कहाँ", "कहां", "कौन", "चाहिए",
    "किसान", "किसानों", "फसल", "बीमा", "दस्तावेज", "समिति", "शिकायत",
    "ऋण", "योजना", "आवेदन", "करें", "जानकारी", "मुझे", "मेरा", "अपने",
    "के", "लिए", "पैक्स", "मिलता", "होता",
}

# Common multilingual stop words (kept small so domain keywords survive)
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "about",
    "as", "into", "or", "and", "but", "if", "not", "do", "does", "did",
    "can", "could", "should", "would", "will", "shall", "may", "might",
    "i", "me", "my", "we", "our", "you", "your", "it", "its", "this",
    "that", "these", "those", "how", "what", "where", "when", "who",
    "which", "why", "please", "tell", "give", "know", "want", "need",
    "का", "की", "के", "को", "में", "से", "पर", "है", "हैं", "और", "या",
    "एक", "यह", "वह", "आहे", "आहेत", "आणि", "किंवा", "मध्ये", "ते", "या",
}

# Cross-lingual keyword bridge so Hindi/Marathi queries still get strong BM25 hits on English docs
CROSS_LINGUAL_EXPANSIONS = {
    "पीक": "crop",
    "विमा": "insurance pmfby",
    "विम्यासाठी": "insurance pmfby apply",
    "फसल": "crop",
    "बीमा": "insurance pmfby",
    "नुकसान": "loss damage claim 72 hours",
    "भरपाई": "claim compensation",
    "हप्ता": "premium installment",
    "प्रीमियम": "premium",
    "कर्ज": "loan credit kcc",
    "कर्जासाठी": "loan credit kcc",
    "ऋण": "loan credit kcc",
    "पॅक्स": "pacs primary agricultural credit society",
    "पैक्स": "pacs primary agricultural credit society",
    "पतसंस्था": "pacs cooperative credit society",
    "खते": "fertilizer",
    "खाद": "fertilizer",
    "बियाणे": "seeds",
    "बीज": "seeds",
    "कागदपत्रे": "documents required 7/12 8a aadhaar",
    "दस्तावेज": "documents required aadhaar passbook",
    "सातबारा": "7/12 satbara land record",
    "७/१२": "7/12 satbara land record",
    "खतौनी": "land record khatauni 7/12",
    "आधार": "aadhaar",
    "पासबुक": "passbook bank",
    "तक्रार": "grievance complaint registrar cpgrams",
    "शिकायत": "grievance complaint registrar cpgrams",
    "निबंधक": "registrar cooperative",
    "रजिस्ट्रार": "registrar cooperative",
    "अधिकार": "member rights voting agm audit bylaws",
    "सभासद": "member membership cooperative",
    "सदस्य": "member membership cooperative",
    "मतदान": "voting one member one vote election",
    "नियम": "rules bylaws mcs act cooperative",
    "योजना": "government schemes subsidy pm-kisan aif ncdc",
    "योजनाएं": "government schemes subsidy pm-kisan aif ncdc",
    "अनुदान": "subsidy scheme",
    "किसान": "farmer kisan pm-kisan",
    "शेतकरी": "farmer pm-kisan namo shetkari",
    "सौर": "solar pump pm-kusum",
    "दुग्ध": "dairy cooperative ncdc",
}

GREETING_PATTERNS = {
    "hi", "hello", "hey", "hii", "hiii", "namaste", "namaskar",
    "good morning", "good afternoon", "good evening",
    "नमस्ते", "नमस्कार", "हॅलो", "हेलो", "राम राम",
}


def normalize_language(lang: str | None) -> str:
    """Normalize language code to one of 'en', 'hi', 'mr'."""
    if not lang:
        return "en"
    code = lang.strip().lower()[:2]
    return code if code in SUPPORTED_LANGUAGES else "en"


def detect_query_language(text: str, requested_language: str | None = None) -> str:
    """
    Determine the response language.
    - If the user typed Devanagari text, check Hindi vs Marathi cues (respecting UI hint when ambiguous).
    - If the user explicitly chose 'hi' or 'mr' in the UI dropdown, honor it so English-typed queries
      still receive answers in the user's selected UI language.
    """
    req = normalize_language(requested_language)
    if not text:
        return req

    # Check if text contains Devanagari characters (\u0900-\u097F)
    devanagari_chars = len(re.findall(r"[\u0900-\u097F]", text))
    if devanagari_chars >= 3:
        tokens = set(tokenize_multilingual(text, remove_stopwords=False))
        mr_hits = len(tokens & MARATHI_CUES)
        hi_hits = len(tokens & HINDI_CUES)
        if mr_hits > hi_hits:
            return "mr"
        if hi_hits > mr_hits:
            return "hi"
        # Ambiguous Devanagari: prefer UI selection if it's hi/mr, else default to hi
        return req if req in ("hi", "mr") else "hi"

    return req


def tokenize_multilingual(text: str, remove_stopwords: bool = True) -> List[str]:
    """
    Unicode-safe tokenizer that preserves English alphanumerics, '7/12', and Devanagari words.
    """
    if not text:
        return []
    lowered = text.lower()
    # Keep 7/12, 8a, numbers, Latin words, and Devanagari sequences
    raw_tokens = re.findall(r"7/12|७/१२|[a-z0-9]+|[\u0900-\u097F]+", lowered)
    if remove_stopwords:
        return [t for t in raw_tokens if len(t) > 1 and t not in STOP_WORDS]
    return raw_tokens


def expand_query_for_bm25(query: str) -> str:
    """Append English equivalents for Devanagari cooperative terms to improve BM25 recall."""
    tokens = tokenize_multilingual(query, remove_stopwords=False)
    extras: List[str] = []
    for tok in tokens:
        if tok in CROSS_LINGUAL_EXPANSIONS:
            extras.append(CROSS_LINGUAL_EXPANSIONS[tok])
    if extras:
        return f"{query} {' '.join(extras)}"
    return query


def is_simple_greeting(query: str) -> bool:
    """Return True if the query is just a short greeting without a substantive question."""
    cleaned = re.sub(r"[!?.,।]+", "", query.strip().lower())
    return cleaned in GREETING_PATTERNS
