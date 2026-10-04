import os
from llm.openai_compatible import OpenAICompatibleLLM

class GeminiLLM(OpenAICompatibleLLM):
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        """
        Gemini API client utilizing its native OpenAI compatibility layer.
        """
        # Resolve Gemini API key from environment if not explicitly passed
        gemini_key = api_key or os.getenv("GEMINI_API_KEY")
        
        # Google Generative AI OpenAI-compatible base URL
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        
        # If no key is set, we pass a dummy so the parent class constructor won't fail immediately,
        # but it will print the error on execution.
        if not gemini_key:
            gemini_key = "MISSING_GEMINI_API_KEY"

        super().__init__(base_url=base_url, api_key=gemini_key, model=model)

    def respond(self, call_state, transcript):
        if self.api_key == "MISSING_GEMINI_API_KEY":
            print("\n[LLM Error] GEMINI_API_KEY environment variable is not set. Falling back to mock response.")
            from llm.mock import MockLLM
            return MockLLM().respond(call_state, transcript)
            
        return super().respond(call_state, transcript)

    def summarize(self, call_state, transcript):
        if self.api_key == "MISSING_GEMINI_API_KEY":
            from llm.mock import MockLLM
            return MockLLM().summarize(call_state, transcript)
            
        return super().summarize(call_state, transcript)
