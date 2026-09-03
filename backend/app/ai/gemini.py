import json
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger
from app.ai.prompts import EMS_SYSTEM_PROMPT, SCOPE_CLASSIFIER_PROMPT

# Attempt to import google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai package not installed or failed to import. Running in mock/fallback mode.")


class GeminiClient:
    """Wrapper around Google Gemini client supporting text generation and structured outputs."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.client = None

        if self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Gemini client with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")
                self.client = None

    async def generate_response(
        self,
        prompt: str,
        system_instruction: str = EMS_SYSTEM_PROMPT,
        temperature: float = 0.2,
        max_output_tokens: int = 1000,
    ) -> str:
        """Generate grounded text response from Gemini."""
        if not self.client:
            logger.info("Using simulated Gemini response (No API key or client unavailable)")
            return self._simulate_gemini_response(prompt)

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            return response.text or "I'm sorry, I couldn't generate an answer based on the current EMS data."
        except Exception as e:
            logger.error(f"Gemini API generation error: {e}")
            raise RuntimeError(f"AI generation temporarily unavailable: {str(e)}")

    async def generate_structured_json(
        self,
        prompt: str,
        system_instruction: str = SCOPE_CLASSIFIER_PROMPT,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Generate structured JSON output from Gemini."""
        if not self.client:
            return self._simulate_structured_classification(prompt)

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                response_mime_type="application/json",
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            raw_text = response.text or "{}"
            return json.loads(raw_text)
        except Exception as e:
            logger.error(f"Gemini structured JSON generation error: {e}")
            return self._simulate_structured_classification(prompt)

    def _simulate_gemini_response(self, prompt: str) -> str:
        """Simulate a grounded response for local testing and development."""
        prompt_lower = prompt.lower()
        if "equinox" in prompt_lower or "summit" in prompt_lower:
            return "The Equinox 2.0 is a 2-day flagship E-Summit scheduled for 30–31 October at MLR Institute of Technology (MLRIT), Hyderabad, organized by Centre for Innovation & Entrepreneurship (CIE)."
        if "ipl" in prompt_lower or "auction" in prompt_lower:
            return "The IPL Auction is a simulated cricket auction sub-event at The Equinox 2.0 where participants manage budgets and bid strategically for players."
        if "monopoly" in prompt_lower or "startup poly" in prompt_lower:
            return "Startup Poly is a Monopoly-inspired fast-paced business simulation sub-event at The Equinox 2.0."
        if "internship" in prompt_lower or "hiring" in prompt_lower:
            return "The Internship Drive connects students directly with hiring startups and companies during The Equinox 2.0."
        if "pitch" in prompt_lower:
            return "Pitch Deck is the flagship pitching competition at The Equinox 2.0 where student founders pitch to investors and mentors."

        return (
            "Here is the event information from EMS:\n\n"
            "Based on our records, the event details and schedules are listed above. "
            "Please ensure you register before the announced deadline and verify all eligibility requirements on the event page."
        )

    def _simulate_structured_classification(self, prompt: str) -> Dict[str, Any]:
        """Local classifier fallback when Gemini client is not initialized."""
        p_lower = prompt.lower()
        if any(k in p_lower for k in ["equinox", "startup", "auction", "pitch", "monopoly", "internship", "selling", "debate", "speaker", "talks"]):
            return {"classification": "IN_SCOPE", "confidence": 0.95, "reason": "Query mentions Equinox 2.0 activity."}
        if any(k in p_lower for k in ["cricket", "score", "weather", "movie", "bitcoin", "president", "homework", "python"]):
            return {"classification": "CLEARLY_OUT_OF_SCOPE", "confidence": 0.96, "reason": "Query matches out-of-scope domain."}
        return {"classification": "AMBIGUOUS", "confidence": 0.50, "reason": "Borderline query."}


gemini_client = GeminiClient()
