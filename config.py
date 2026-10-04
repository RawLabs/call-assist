import os

# Load configuration values from environment variables or defaults
LLM_TYPE = os.getenv("LLM_TYPE", "openai_compatible").lower()  # "mock", "openai_compatible", "gemini"
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "lm-studio")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-3b-instruct-q4_k_m")

STT_TYPE = os.getenv("STT_TYPE", "whisper").lower()  # "mock", "whisper"
STT_WHISPER_MODEL = os.getenv("STT_WHISPER_MODEL", "tiny")

TTS_TYPE = os.getenv("TTS_TYPE", "pyttsx3").lower()  # "mock", "pyttsx3"

VAD_THRESHOLD = float(os.getenv("VAD_THRESHOLD", "300.0"))
DB_PATH = os.getenv("DB_PATH", "calls.db")

# Factory functions
def get_llm():
    if LLM_TYPE == "openai_compatible":
        from llm.openai_compatible import OpenAICompatibleLLM
        return OpenAICompatibleLLM(base_url=LLM_BASE_URL, api_key=LLM_API_KEY, model=LLM_MODEL)
    elif LLM_TYPE == "gemini":
        from llm.gemini import GeminiLLM
        return GeminiLLM(api_key=LLM_API_KEY, model=LLM_MODEL)
    else:
        from llm.mock import MockLLM
        return MockLLM()

def get_stt():
    if STT_TYPE == "whisper":
        from stt.whisper import WhisperSTT
        return WhisperSTT(model_size=STT_WHISPER_MODEL)
    else:
        from stt.mock import MockSTT
        return MockSTT()

def get_tts():
    if TTS_TYPE == "pyttsx3":
        from tts.pyttsx3 import PyTTSx3TTS
        return PyTTSx3TTS()
    else:
        from tts.mock import MockTTS
        return MockTTS()

def get_vad():
    from audio.rms_vad import RMSVoiceActivityDetector
    return RMSVoiceActivityDetector(threshold=VAD_THRESHOLD)

def get_db():
    from storage.call_db import CallDatabase
    return CallDatabase(db_path=DB_PATH)
