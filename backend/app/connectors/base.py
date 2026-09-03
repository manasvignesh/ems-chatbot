from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.event import EventKnowledge


class BaseEventConnector(ABC):
    """Abstract interface for event data sources."""

    @abstractmethod
    async def fetch_public_events(self) -> List[EventKnowledge]:
        """Fetch all currently public, approved events from the source."""
        pass

    @abstractmethod
    async def fetch_public_event(self, event_id: str) -> Optional[EventKnowledge]:
        """Fetch a specific event by ID or slug."""
        pass
