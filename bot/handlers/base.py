from abc import ABC, abstractmethod
from typing import Optional
from ..context import UserContext

class BaseHandler(ABC):
    @abstractmethod
    def should_handle(self, context: UserContext, message: str) -> bool:
        """Determines if this handler should process the current request context."""
        pass

    @abstractmethod
    def handle(self, context: UserContext, message: str) -> str:
        """Processes the message and returns the response."""
        pass
