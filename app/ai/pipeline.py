"""AI processing pipeline: raw source item -> structured citizen content."""
import logging

from .gemini import ask_gemini

logger = logging.getLogger("citizeneye.pipeline")


def _fallback(title: str, source_name: str) -> dict:
    """Deterministic placeholder used when Gemini is unavailable.
    Keeps the system functional without an API key (dev/demo mode)."""
    return {
        "title": title[:500],
        "summary": f"A new update was detected from {source_name}: \"{title}\". Full AI simplification is pending.",
        "full_text": (
            f"The Digital Eye detected new content published by {source_name}.\n\n"
            f"Title: {title}\n\n"
            "This item was collected automatically. Once AI processing is enabled "
            "(GEMINI_API_KEY configured), this section will contain a simplified, "
            "citizen-friendly breakdown of what happened, what it means, and who may be affected."
        ),
        "jurisdiction": "",
        "plain_explanation": "A plain-language explanation is not available until the source is processed.",
        "original_wording": "",
        "law_citation": source_name,
        "amendment_history": "Amendment history not found in the source.",
        "topic": "general",
        "rights_impact": "",
        "dyk_text": f"Did you know? New civic update from {source_name}.",
        "sms_text": f"CivicPulse: New update from {source_name}: {title[:80]}",
        "source_reference": "",
        "source_quote": "",
    }


def process_content(title: str, url: str, source_name: str, content: str = "") -> dict:
    prompt = (
        f"Source name: {source_name}\n"
        f"Source URL: {url}\n"
        f"Content title: {title}\n\n"
        f"Source text:\n{content[:12000]}\n\n"
        "Process this into the JSON format specified."
    )
    result = ask_gemini(prompt)
    if not result:
        return _fallback(title, source_name)

    return {
        "title": title[:500],
        "summary": result.get("summary", ""),
        "full_text": result.get("full_text", ""),
        "jurisdiction": result.get("jurisdiction", ""),
        "plain_explanation": result.get("plain_explanation", ""),
        "original_wording": result.get("original_wording", ""),
        "law_citation": result.get("law_citation", ""),
        "amendment_history": result.get("amendment_history", "Amendment history not found in the source."),
        "topic": result.get("topic", "general"),
        "rights_impact": result.get("rights_impact", ""),
        "dyk_text": result.get("dyk_text", ""),
        "sms_text": result.get("sms_text", ""),
        "source_reference": result.get("source_reference", ""),
        "source_quote": result.get("source_quote", ""),
    }
