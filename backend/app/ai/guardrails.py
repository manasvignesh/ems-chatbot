import re
from typing import Tuple

# Common prompt injection, system prompt extraction, or credential sniffing patterns
PROMPT_INJECTION_PATTERNS = [
    r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)\b",
    r"(?i)\bforget\s+(the\s+)?(guardrails|instructions|system\s+prompt|rules)\b",
    r"(?i)\b(reveal|show|print|tell|give\s+me|expose)\s+(your\s+)?(system\s+prompt|hidden\s+prompt|instructions|initial\s+prompt)\b",
    r"(?i)\b(reveal|show|print|tell|give\s+me|what\s+is)\s+.*?\b(api\s*key|gemini\s*key|supabase.*key|service\s*role.*key|service\s*role|token|secret|credentials|password)\b",
    r"(?i)\bact\s+as\s+(an?\s+)?(unrestricted|jailbroken|dan|evil|developer\s+mode)\b",
    r"(?i)\bpretend\s+(you\s+are|to\s+be)\s+(an?\s+)?(unrestricted|admin|database\s+admin|root)\b",
    r"(?i)\b(drop\s+table|select\s+\*\s+from|insert\s+into|delete\s+from|union\s+select)\b",
    r"(?i)\bshow\s+(hidden|unpublished|private|secret)\s+(events|tables|columns|users|data)\b",
]

COMPILED_INJECTION_PATTERNS = [re.compile(p) for p in PROMPT_INJECTION_PATTERNS]


def detect_prompt_injection(query: str) -> Tuple[bool, str]:
    """Detect if the user query contains prompt injection or credential extraction attempts."""
    if not query:
        return False, ""

    for pattern in COMPILED_INJECTION_PATTERNS:
        if pattern.search(query):
            return True, "Potential prompt injection or credential leak attempt detected."

    return False, ""


def sanitize_retrieved_context(context_text: str) -> str:
    """Ensure retrieved document text is treated strictly as passive data and cannot inject instructions."""
    if not context_text:
        return ""
    # Strip any pseudo system tags that malicious PDFs might contain
    sanitized = re.sub(r"(?i)<\s*(system|instruction|rules|admin)[^>]*>", "[CONTENT_BLOCK]", context_text)
    sanitized = re.sub(r"(?i)<\s*/\s*(system|instruction|rules|admin)\s*>", "[/CONTENT_BLOCK]", sanitized)
    return sanitized
