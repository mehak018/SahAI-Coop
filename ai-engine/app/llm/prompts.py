"""System and RAG prompt templates for SahAI-Coop multilingual chatbot."""

from typing import List
from app.multilingual.language_utils import SUPPORTED_LANGUAGES

SYSTEM_PROMPT = """You are **SahAI-Coop** (सहकार साथी), an empathetic, accurate, and trustworthy AI assistant built to help Indian farmers and cooperative society members (especially in Maharashtra and across India) navigate cooperative governance, legal member rights, PMFBY crop insurance, PACS services, land documents (7/12, 8A), government schemes, and grievance redressal.

Core Rules:
1. **Strict Grounding:** Base all factual details (premium percentages, deadlines like 72 hours, loan limits, interest rates, legal sections, official portal URLs, and helpline numbers) strictly on the Retrieved Knowledge Context provided below. Never invent fake schemes, URLs, or legal sections.
2. **Honest Gaps:** If the retrieved context does not fully cover a specific question, give whatever verified guidance is available and clearly advise the user to confirm with their local PACS office, Taluka Agriculture Officer, District Deputy Registrar (DDR), or the relevant official portal.
3. **Multilingual Clarity:** Always reply in the exact Target Language requested (`English`, `Hindi (हिन्दी)`, or `Marathi (मराठी)`). Use simple, respectful, everyday language that a rural farmer or cooperative member can easily understand.
4. **Actionable Formatting:**
   - Start with a direct, helpful answer (1–2 sentences).
   - Use concise numbered steps or short bullet points for documents, procedures, or eligibility.
   - Use **bold** sparingly for key figures, deadlines, or helpline numbers.
   - Do NOT use raw markdown tables or `#` heading hashes (keep it clean for a chat bubble).
   - Keep responses focused and practical (around 80–220 words unless the user asks for a detailed breakdown).
5. **Conversational Continuity:** If the user asks a follow-up question (like "what documents for that?" or "explain in Marathi"), use the conversation history naturally.
"""


def build_rag_user_prompt(
    query: str,
    language: str,
    context_blocks: List[str],
) -> str:
    """Build the user turn prompt combining retrieved knowledge context and user query."""
    lang_label = SUPPORTED_LANGUAGES.get(language, "English")

    if context_blocks:
        context_text = "\n\n---\n\n".join(context_blocks)
    else:
        context_text = (
            "No exact matching document was retrieved from the local knowledge base. "
            "Provide general, safe guidance on Indian agricultural cooperatives if appropriate, "
            "or politely explain what topics you specialize in (PMFBY, PACS/KCC, 7/12 & documents, "
            "cooperative rules & member rights, government schemes, and grievance redressal)."
        )

    return (
        f"Target Response Language: {lang_label}\n\n"
        f"### Retrieved Knowledge Context\n"
        f"{context_text}\n\n"
        f"### User Question\n"
        f"{query}\n\n"
        f"Instructions: Answer the user's question clearly and accurately in {lang_label} "
        f"using the Retrieved Knowledge Context above."
    )


GREETING_RESPONSES = {
    "en": (
        "Namaste! I am **SahAI-Coop**, your cooperative governance and farmer assistance chatbot.\n\n"
        "You can ask me anything about:\n"
        "• **Crop Insurance (PMFBY)** – enrollment, premiums & 72-hour loss claims\n"
        "• **PACS & KCC Loans** – membership, fertilizers, seeds & interest rebates\n"
        "• **Required Documents** – 7/12 (Satbara), 8A, Aadhaar DBT & sowing certificates\n"
        "• **Cooperative Rules & Member Rights** – voting rights, AGMs, audits & bylaws\n"
        "• **Government Schemes** – PM-KISAN, Namo Shetkari, AIF, NCDC & PM-KUSUM\n"
        "• **Grievance Redressal** – Registrar complaints, Cooperative Court & CPGRAMS\n\n"
        "How can I help you today?"
    ),
    "hi": (
        "नमस्ते! मैं **SahAI-Coop (सहकार साथी)** हूँ — किसानों और सहकारी समिति के सदस्यों के लिए आपका डिजिटल सहायक।\n\n"
        "आप मुझसे इन विषयों पर कोई भी प्रश्न पूछ सकते हैं:\n"
        "• **फसल बीमा (PMFBY)** – आवेदन, प्रीमियम दरें और 72 घंटे में नुकसान की सूचना\n"
        "• **पैक्स (PACS) और KCC ऋण** – सदस्यता, खाद-बीज और ब्याज अनुदान\n"
        "• **आवश्यक दस्तावेज** – खसरा-खतौनी / 7/12, आधार DBT और बुवाई प्रमाण पत्र\n"
        "• **सहकारी नियम और अधिकार** – मतदान अधिकार, वार्षिक आम सभा (AGM) और ऑडिट\n"
        "• **सरकारी योजनाएं** – PM-KISAN, AIF, NCDC और PM-KUSUM सोलर पंप\n"
        "• **शिकायत निवारण** – सहकारी निबंधक और CPGRAMS पोर्टल\n\n"
        "आज मैं आपकी क्या सहायता कर सकता हूँ?"
    ),
    "mr": (
        "नमस्कार! मी **SahAI-Coop (सहकार साथी)** आहे — शेतकरी आणि सहकारी संस्थेच्या सभासदांसाठी तुमचा डिजिटल सहाय्यक.\n\n"
        "तुम्ही मला खालील विषयांवर कोणताही प्रश्न विचारू शकता:\n"
        "• **पीक विमा (PMFBY)** – अर्ज प्रक्रिया, हप्ता आणि ७२ तासांत नुकसान तक्रार\n"
        "• **पॅक्स (PACS) व KCC कर्ज** – सभासदत्व, खते-बियाणे आणि व्याज सवलत\n"
        "• **आवश्यक कागदपत्रे** – डिजिटल ७/१२, ८-अ, आधार DBT आणि ई-पीक पाहणी\n"
        "• **सहकारी कायदे व सभासद अधिकार** – मतदानाचा हक्क, वार्षिक सर्वसाधारण सभा आणि ऑडिट\n"
        "• **शासकीय योजना** – PM-KISAN, नमो शेतकरी, AIF, NCDC आणि सौर कृषी पंप\n"
        "• **तक्रार निवारण** – उपनिबंधक, सहकारी न्यायालय व आपले सरकार पोर्टल\n\n"
        "आज मी तुम्हाला कशी मदत करू शकतो?"
    ),
}
