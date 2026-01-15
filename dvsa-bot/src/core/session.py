from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from ..config.settings import TestPreferences

@dataclass
class SessionData:
    preferences: TestPreferences
    start_time: datetime = field(default_factory=datetime.now)
    current_centre_index: int = 0
    refresh_url: Optional[str] = None
    attempts: int = 0
    errors: List[str] = field(default_factory=list)
    
    def get_current_centre(self):
        if self.current_centre_index < len(self.preferences.preferred_centres):
            return self.preferences.preferred_centres[self.current_centre_index]
        return self.preferences.preferred_centres[0]
    
    def move_to_next_centre(self):
        self.current_centre_index += 1
        if self.current_centre_index >= len(self.preferences.preferred_centres):
            self.current_centre_index = 0
            return False
        return True
    
    def add_error(self, error: str):
        self.errors.append(f"{datetime.now()}: {error}")
    
    def increment_attempts(self):
        self.attempts += 1
