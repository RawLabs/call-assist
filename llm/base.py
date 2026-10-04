from state.call_state import CallState
from state.models import LLMSuggestion

class LanguageModel:
    def respond(self, call_state: CallState, transcript: list) -> LLMSuggestion:
        """
        Generates a conversational response and extracts structural information based on the current
        call state and transcript history.
        
        transcript: list of dicts [{"sender": "caller"|"assistant", "text": "..."}]
        Returns:
            An LLMSuggestion instance containing the text to speak and any extracted metadata.
        """
        raise NotImplementedError("LLM implementations must implement respond")

    def summarize(self, call_state: CallState, transcript: list) -> str:
        """
        Generates a final, structured markdown intake summary card for the employee.
        
        Returns:
            A string containing the markdown summary card.
        """
        raise NotImplementedError("LLM implementations must implement summarize")
