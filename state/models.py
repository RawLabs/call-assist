from pydantic import BaseModel, Field

class ExtractedInfo(BaseModel):
    caller_name: str | None = None
    callback_number: str | None = None
    request: str | None = None
    callback_preference: str | None = None
    details: dict[str, str | None] = Field(default_factory=dict)

class LLMSuggestion(BaseModel):
    say: str
    intent: str | None = None
    route: str | None = None
    extracted: ExtractedInfo = Field(default_factory=ExtractedInfo)
    needs_more_information: bool = True
