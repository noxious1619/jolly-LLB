# app/memory.py

from typing import Dict
from app.extractor import UserProfile


class ConversationMemory:
    """
    Maintains and updates user profile across multiple conversation turns.
    """

    def __init__(self):
        self.profile = UserProfile()

    def merge_profile(self, new_data: UserProfile) -> UserProfile:
        """
        Merge new extracted data into existing profile.
        Only updates fields that are not None.
        """

        existing_data = self.profile.model_dump()
        incoming_data = new_data.model_dump()

        for key, value in incoming_data.items():
            if value is not None:
                existing_data[key] = value

        # Rebuild profile
        self.profile = UserProfile(**existing_data)

        return self.profile

    def get_profile(self) -> UserProfile:
        return self.profile

    def reset(self):
        """
        Clear conversation state.
        """
        self.profile = UserProfile()