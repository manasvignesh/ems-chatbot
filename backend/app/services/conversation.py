import re
from typing import Dict, List, Optional
from collections import defaultdict
from app.models.chat import ChatMessage
from app.core.config import settings


class ConversationManager:
    """Manages bounded in-memory conversation history and entity resolution for pronoun follow-ups."""

    def __init__(self, max_history: int = settings.MAX_CONVERSATION_HISTORY_MESSAGES):
        self.max_history = max_history
        self.sessions: Dict[str, List[ChatMessage]] = defaultdict(list)
        self.last_entities: Dict[str, str] = {}  # conversation_id -> last referenced event name

    def add_message(self, conversation_id: str, role: str, content: str):
        """Append message and truncate to bounded window."""
        self.sessions[conversation_id].append(ChatMessage(role=role, content=content))
        if len(self.sessions[conversation_id]) > self.max_history:
            self.sessions[conversation_id] = self.sessions[conversation_id][-self.max_history:]

        # Detect and store entity mentioned
        if role == "assistant" or role == "user":
            found = self._extract_event_mention(content)
            if found:
                self.last_entities[conversation_id] = found

    def get_history(self, conversation_id: str) -> List[ChatMessage]:
        return self.sessions.get(conversation_id, [])

    def format_history_for_prompt(self, conversation_id: str) -> str:
        """Format bounded conversation history for LLM prompt."""
        history = self.get_history(conversation_id)
        if not history:
            return ""
        lines = []
        for msg in history:
            lines.append(f"{msg.role.upper()}: {msg.content}")
        return "\n".join(lines)

    def resolve_query_context(self, query: str, conversation_id: str) -> str:
        """Resolve pronouns like 'it', 'this event', 'that workshop' if an active entity was tracked."""
        last_entity = self.last_entities.get(conversation_id)
        if not last_entity:
            return query

        lower_q = query.lower()
        pronoun_triggers = [
            r"\bit\b",
            r"\bthis\b",
            r"\bthat\b",
            r"\bthis event\b",
            r"\bthat event\b",
            r"\bthe workshop\b",
            r"\bthe hackathon\b",
        ]

        if any(re.search(p, lower_q) for p in pronoun_triggers) and last_entity.lower() not in lower_q:
            # Append entity context hint
            return f"{query} (referring to {last_entity})"

        return query

    def clear_conversation(self, conversation_id: str):
        if conversation_id in self.sessions:
            del self.sessions[conversation_id]
        if conversation_id in self.last_entities:
            del self.last_entities[conversation_id]

    def _extract_event_mention(self, text: str) -> Optional[str]:
        known_events = [
            "HackVerse",
            "Hands-on IoT & Embedded Systems Workshop",
            "Autonomous AI Agents & GenAI Bootcamp",
            "CyberShield CTF",
            "CIE Innovation Summit",
        ]
        for e in known_events:
            if e.lower() in text.lower():
                return e
        return None


conversation_manager = ConversationManager()
