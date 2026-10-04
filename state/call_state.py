from pydantic import BaseModel, Field
from state.models import ExtractedInfo

class CallState(BaseModel):
    caller_name: str | None = None
    callback_number: str | None = None
    intent: str | None = None
    department: str | None = None
    request: str | None = None
    callback_preference: str | None = None
    details: dict[str, str] = Field(default_factory=dict)
    silence_count: int = 0
    clarification_failures: int = 0

    def merge_extracted(self, extracted: ExtractedInfo):
        for field in ("caller_name", "callback_number", "request", "callback_preference"):
            value = getattr(extracted, field)
            if value:
                setattr(self, field, value)
        self.details.update({key: value for key, value in extracted.details.items() if value})

    def is_complete(self) -> bool:
        return bool(self.caller_name and self.callback_number and self.request)
