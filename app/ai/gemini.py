"""Google Gemini client wrapper."""
import json
import logging

from ..config import settings

logger = logging.getLogger("citizeneye.ai")

SYSTEM_INSTRUCTIONS = """You are the CivicPulse AI processor for CitizenEye, a Ugandan civic information platform.

Rules you MUST follow:
- Use ONLY the information provided from the verified source.
- Do NOT invent facts or add information not supported by the source content.
- Explain in simple language an ordinary citizen understands.
- Identify what happened, why it may matter, and who may be affected — only if supported by the source.
- Say what happens next ONLY if the source supports it.
- If the source is from another country, identify that country clearly and describe it as a comparison.
- Never present another country's law as if it applies in Uganda.
- Separate the plain-language explanation from the source's exact legal wording.
- Quote only wording present in the supplied source text; otherwise return an empty quotation.
- Give a precise citation when the source provides one.
- Report amendment dates and changes only when the source provides them; otherwise say "Amendment history not found in the source."

You will receive a title from a trusted source page. Respond with ONLY valid JSON in this exact format:
{
  "summary": "2-3 sentence simple explanation of what happened and why it matters",
  "full_text": "4-8 sentence citizen-friendly breakdown: what happened, what it means, who is affected",
    "jurisdiction": "country or legal system this law belongs to",
    "plain_explanation": "simple explanation of the rule and a concrete example",
    "original_wording": "short exact quotation from the source, or empty string if unavailable",
    "law_citation": "official law name, section/article, date, and source citation if available",
    "amendment_history": "what changed and when, or Amendment history not found in the source.",
    "topic": "one of: parliament, privacy, labor, land, police, education, business, health, comparative, general",
  "rights_impact": "the related right or law reference if clearly connected, else empty string",
  "dyk_text": "one-sentence 'Did you know? ...' hook about this update",
  "sms_text": "CivicPulse: one short SMS version under 160 characters"
}"""

# Lazy import so the server works without google-genai installed / no key
_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def ask_gemini(prompt: str) -> dict | None:
    """Ask Gemini to process source content. Returns parsed JSON or None on failure."""
    if not settings.gemini_api_key or settings.gemini_api_key.startswith("your-"):
        logger.warning("GEMINI_API_KEY not set; AI processing skipped")
        return None
    try:
        client = _get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"system_instruction": SYSTEM_INSTRUCTIONS},
        )
        text = response.text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as exc:
        logger.error("Gemini call failed: %s", exc)
        return None
