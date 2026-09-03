from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class PageContext(BaseModel):
    """Context sent by the frontend widget representing the user's current page."""
    page_type: Optional[str] = Field("home", description="Page type: 'event', 'category', 'home', etc.")
    event_id: Optional[str] = Field(None, description="Current event ID or slug if on an event page")
    event_name: Optional[str] = Field(None, description="Event name if on an event page")
    pathname: Optional[str] = Field(None, description="Current browser window pathname")


class ChatMessage(BaseModel):
    """Single chat message in conversation history."""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """Payload for POST /api/chat."""
    bot_id: str = Field("ems", description="Target bot identifier")
    message: str = Field(..., min_length=1, max_length=2000, description="User's query")
    conversation_id: Optional[str] = Field(None, description="Session conversation ID")
    conversation_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Prior conversation messages")
    page_context: Optional[PageContext] = Field(None, description="Current page context")


class EventCard(BaseModel):
    """Compact event reference card displayed inside the widget."""
    type: str = "event"
    event_id: str
    title: str
    date: Optional[str] = None
    venue: Optional[str] = None
    organizer: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None


class SourceReference(BaseModel):
    """User-friendly source reference for retrieved facts."""
    title: str
    source_type: str
    url: Optional[str] = None


class ScopeClassificationResult(BaseModel):
    """Structured scope evaluation with granular classification levels."""
    classification: Literal[
        "IN_SCOPE",
        "LIKELY_IN_SCOPE",
        "AMBIGUOUS",
        "SUSPICIOUS",
        "CLEARLY_OUT_OF_SCOPE"
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    clarification_prompt: Optional[str] = None


class ChatResponseSuccess(BaseModel):
    status: Literal["success"] = "success"
    conversation_id: str
    answer: str
    sources: List[SourceReference] = Field(default_factory=list)
    cards: List[EventCard] = Field(default_factory=list)


class ChatResponseOutOfScope(BaseModel):
    status: Literal["out_of_scope"] = "out_of_scope"
    conversation_id: str
    classification_level: Literal["SUSPICIOUS", "CLEARLY_OUT_OF_SCOPE"] = "CLEARLY_OUT_OF_SCOPE"
    warning_type: str = "invalid_event_pass"
    ticket_number: Optional[str] = "EQX-PASS-403"
    cooldown_seconds: int = 3
    reason: Optional[str] = "Query is outside the scope of The Equinox 2.0."
    message: Optional[str] = "This assistant is focused on The Equinox 2.0. Ask me about events, dates, sub-events, venue, sponsorship, or contacts."


class ChatResponseError(BaseModel):
    status: Literal["error"] = "error"
    message: str
