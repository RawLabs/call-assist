import json
from state.call_state import CallState
from state.models import LLMSuggestion
from business import BusinessProfile, load_business_profile
from llm.base import LanguageModel
from storage.call_db import CallDatabase

class CallController:
    def __init__(self, llm: LanguageModel, db: CallDatabase, profile: BusinessProfile | None = None):
        self.profile = profile or load_business_profile()
        self.llm = llm
        self.db = db
        self.state = CallState()
        self.transcript = []
        self.active = False

    def initialize_call(self) -> str:
        """Starts a new call session, resets state, and returns the greeting."""
        self.state = CallState()
        self.transcript = []
        self.active = True
        greeting = self.profile.greeting
        self.transcript.append({"sender": "assistant", "text": greeting})
        return greeting

    def process_caller_input(self, text: str) -> str:
        """
        Processes a caller utterance.
        Updates state, evaluates validation rules/escapes, and returns the TTS response.
        """
        if not self.active:
            return "No active call session. Please start a call first."

        cleaned_text = text.strip()
        
        # 1. Check for manual operator request
        if cleaned_text.lower() in ["operator", "human", "person", "help me please"]:
            self.state.department = "HUMAN"
            self.state.intent = "GENERAL"
            response = "Understood. I have marked your request for a human operator."
            self.transcript.append({"sender": "caller", "text": cleaned_text})
            self.transcript.append({"sender": "assistant", "text": response})
            self.save_and_terminate()
            return response

        # 2. Check for silence
        if not cleaned_text:
            self.state.silence_count += 1
            self.transcript.append({"sender": "caller", "text": "<silence>"})
            
            if self.state.silence_count == 1:
                response = "Are you still there? I didn't catch that."
                self.transcript.append({"sender": "assistant", "text": response})
                return response
            else:
                self.state.department = "HUMAN"
                response = "Since I am having trouble hearing you, I will mark your request for a human operator. Goodbye."
                self.transcript.append({"sender": "assistant", "text": response})
                self.save_and_terminate()
                return response
        else:
            # Reset silence counter upon receiving input
            self.state.silence_count = 0

        self.transcript.append({"sender": "caller", "text": cleaned_text})

        # 3. Request suggestion from LLM adapter
        suggestion: LLMSuggestion = self.llm.respond(self.state, self.transcript)

        # 4. Compare state before and after to check if new information was successfully captured
        old_state_dump = json.dumps(self.state.model_dump())
        
        self.state.merge_extracted(suggestion.extracted)
        if suggestion.intent in self.profile.departments:
            self.state.intent = suggestion.intent

        new_state_dump = json.dumps(self.state.model_dump())
        state_changed = (old_state_dump != new_state_dump)

        # 5. Handle clarification failures
        # If assistant is asking for more info, but caller's response failed to yield new state details
        if suggestion.needs_more_information and not state_changed:
            self.state.clarification_failures += 1
            if self.state.clarification_failures >= 2:
                self.state.department = "HUMAN"
                response = "I'm having some trouble collecting those details. I will mark your request for a human representative."
                self.transcript.append({"sender": "assistant", "text": response})
                self.save_and_terminate()
                return response
        else:
            self.state.clarification_failures = 0

        # Only configured departments can receive completed intake requests.
        # HUMAN is an escape route and does not require complete contact details.
        if suggestion.route == "HUMAN":
            self.state.department = "HUMAN"
        elif self.state.is_complete():
            target = suggestion.route or self.state.intent
            if self.profile.accepts_route(target):
                self.state.department = target

        if self.state.department:
            response = f"Thank you. I have saved your message for {self.state.department}."
            self.transcript.append({"sender": "assistant", "text": response})
            self.save_and_terminate()
            return response

        if suggestion.route:
            suggestion.say = "Before I save your message, could you provide your name, callback number, and request?"

        # 7. No routing triggered, continue conversation
        self.transcript.append({"sender": "assistant", "text": suggestion.say})
        return suggestion.say

    def save_and_terminate(self):
        """Ends the call, logs summary cards to DB, and marks session inactive."""
        self.active = False
        summary = self.llm.summarize(self.state, self.transcript)
        self.db.save_call(self.state, self.transcript, summary)
