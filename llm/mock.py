"""Deterministic intake demo; live models handle natural-language extraction."""
import re
from business import BusinessProfile, load_business_profile
from state.call_state import CallState
from state.models import LLMSuggestion, ExtractedInfo
from llm.base import LanguageModel

class MockLLM(LanguageModel):
    def __init__(self, profile: BusinessProfile | None = None):
        self.profile = profile or load_business_profile()

    def respond(self, call_state: CallState, transcript: list) -> LLMSuggestion:
        text = next((turn["text"] for turn in reversed(transcript) if turn["sender"] == "caller"), "").strip()
        lower = text.lower()
        if re.search(r"\b(hours|open|closed)\b", lower):
            return LLMSuggestion(say=self.profile.hours or "I don't have confirmed hours. I can take a message so someone can help.", needs_more_information=False)
        extracted = ExtractedInfo()
        phone = re.search(r"(?<!\d)(?:\+\d{1,3}[ -]?)?(?:\(\d{3}\)|\d{3})[ -]?\d{3}[ -]?\d{4}(?!\d)", text)
        if phone:
            extracted.callback_number = phone.group()
        name = re.search(r"(?:my name is|name:)\s*([^,.!?]+)", text, re.I)
        if name:
            extracted.caller_name = name.group(1).strip()
        elif call_state.request and not call_state.caller_name and not phone:
            if re.fullmatch(r"[A-Za-z]+(?:[ '-][A-Za-z]+){0,3}", text):
                extracted.caller_name = text
        intent = call_state.intent or "GENERAL"
        keywords = {
            "SALES": ("quote", "buy", "sales", "pricing"),
            "SUPPORT": ("help", "problem", "support", "broken"),
            "APPOINTMENTS": ("appointment", "schedule", "booking"),
        }
        for department, description in self.profile.departments.items():
            terms = (department.lower(),) + keywords.get(department, ())
            if any(re.search(r"\b" + re.escape(term) + r"\b", lower) for term in terms):
                intent = department
                break
        if not call_state.request and not name and not phone:
            extracted.request = text
        pending = call_state.model_copy(deep=True)
        pending.merge_extracted(extracted)
        if not pending.request:
            say = "What would you like help with?"
        elif not pending.caller_name:
            say = "May I have your name?"
        elif not pending.callback_number:
            say = "What is the best callback number for you?"
        else:
            say = "Thank you. I have the details for your message."
        return LLMSuggestion(say=say, intent=intent, extracted=extracted,
                             needs_more_information=not pending.is_complete())

    def summarize(self, call_state: CallState, transcript: list) -> str:
        details = "\n".join(f"- {key}: {value}" for key, value in call_state.details.items())
        return (f"### CALLBACK / MESSAGE\n\n"
                f"Caller: {call_state.caller_name or 'Unknown'}\n"
                f"Phone: {call_state.callback_number or 'Unknown'}\n"
                f"Request: {call_state.request or 'Not provided'}\n"
                f"Callback preference: {call_state.callback_preference or 'Not provided'}\n"
                f"Department: {call_state.department or 'HUMAN'}\n{details}")
