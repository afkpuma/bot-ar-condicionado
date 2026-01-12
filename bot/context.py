from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .states import ConversationState

@dataclass
class UserContext:
    phone: str
    state: ConversationState
    data: Dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_state(self, new_state: ConversationState):
        self.state = new_state
        self.updated_at = datetime.now()

    def update_data(self, **kwargs):
        self.data.update(kwargs)
        self.updated_at = datetime.now()
