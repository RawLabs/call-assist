"""Business configuration shared by demos, intake rules, and model prompts."""
import json
import os
from pydantic import BaseModel, Field

class BusinessProfile(BaseModel):
    name: str = "CallAssist"
    description: str = "a business or personal phone line"
    hours: str | None = None
    departments: dict[str, str] = Field(default_factory=lambda: {
        "SALES": "Product inquiries, quotes, and new business",
        "SUPPORT": "Help with an existing product or service",
        "APPOINTMENTS": "Appointment and scheduling requests",
        "GENERAL": "Other inquiries and messages",
    })

    @property
    def greeting(self) -> str:
        return f"Thanks for calling {self.name}. How can I help? You can ask for a human at any time."

    def accepts_route(self, route: str | None) -> bool:
        return route == "HUMAN" or route in self.departments


def load_business_profile() -> BusinessProfile:
    path = os.getenv("BUSINESS_PROFILE")
    if path:
        with open(path) as source:
            return BusinessProfile.model_validate(json.load(source))
    return BusinessProfile()
