from tts.base import TextToSpeech

class MockTTS(TextToSpeech):
    def __init__(self):
        self.history = []

    def speak(self, text: str) -> None:
        """Prints the text to the terminal, simulating TTS playback."""
        self.history.append(text)
        print(f"AI (Mock TTS): \"{text}\"")
