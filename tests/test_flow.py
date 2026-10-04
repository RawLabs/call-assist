import pytest
from business import BusinessProfile
from controller.call_controller import CallController
from llm.mock import MockLLM
from state.models import LLMSuggestion, ExtractedInfo
from storage.call_db import CallDatabase

@pytest.fixture
def controller():
    return CallController(MockLLM(), CallDatabase(":memory:"))

@pytest.mark.parametrize("message, department", [
    ("I'd like a quote", "SALES"),
    ("I need support with my order", "SUPPORT"),
    ("I'd like an appointment", "APPOINTMENTS"),
    ("Please call me about my inquiry", "GENERAL"),
])
def test_complete_intake(controller, message, department):
    controller.initialize_call()
    assert "name" in controller.process_caller_input(message).lower()
    assert "callback" in controller.process_caller_input("My name is Alex Rivera").lower()
    controller.process_caller_input("303-555-0123")
    assert not controller.active
    assert controller.state.department == department
    saved = controller.db.get_all_calls()
    assert len(saved) == 1
    assert saved[0]["state_json"]["request"] == message
    assert "Alex Rivera" in saved[0]["summary"]

@pytest.mark.parametrize("utterances", [["operator"], ["", ""],
    ["I need support", "why aren't you helping me", "why aren't you helping me"]])
def test_human_fallback(controller, utterances):
    controller.initialize_call()
    for text in utterances:
        controller.process_caller_input(text)
    assert not controller.active
    assert controller.state.department == "HUMAN"
    assert len(controller.db.get_all_calls()) == 1

def test_hours_are_not_invented(controller):
    controller.initialize_call()
    assert "confirmed hours" in controller.process_caller_input("What are your hours?")
    assert controller.state.request is None

def test_custom_business():
    profile = BusinessProfile(name="River Office", hours="Weekdays 9–4", departments={"RECEPTION": "Messages"})
    controller = CallController(MockLLM(profile), CallDatabase(":memory:"), profile)
    assert "River Office" in controller.initialize_call()
    assert controller.process_caller_input("hours") == "Weekdays 9–4"
    controller.process_caller_input("Reception please")
    controller.process_caller_input("Alex Rivera")
    controller.process_caller_input("303-555-0123")
    assert controller.state.department == "RECEPTION"

@pytest.mark.parametrize("route", ["SALES", "UNCONFIGURED"])
def test_model_cannot_route_incomplete_intake(controller, route):
    controller.llm.respond = lambda *_: LLMSuggestion(say="Transferred", route=route)
    controller.initialize_call()
    controller.process_caller_input("Hello")
    assert controller.active
    assert controller.state.department is None

def test_unknown_route_is_rejected(controller):
    controller.llm.respond = lambda *_: LLMSuggestion(say="Transferred", route="UNKNOWN",
        extracted=ExtractedInfo(caller_name="Alex", callback_number="303-555-0123", request="Question"))
    controller.initialize_call()
    controller.process_caller_input("Hello")
    assert controller.active
    assert controller.state.department is None

def test_optional_details_merge(controller):
    controller.state.merge_extracted(ExtractedInfo(details={"account": "123", "unused": None}))
    controller.state.merge_extracted(ExtractedInfo(details={"account": None, "topic": "renewal"}))
    assert controller.state.details == {"account": "123", "topic": "renewal"}
