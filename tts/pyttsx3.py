from tts.base import TextToSpeech

class PyTTSx3TTS(TextToSpeech):
    def __init__(self, rate: int = 160):
        self.rate = rate
        self.engine = None

    def speak(self, text: str) -> None:
        """Synthesizes text and speaks it using pyttsx3 offline."""
        if not text:
            return

        if self.engine is None:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", self.rate)
            except ImportError:
                print("\n[TTS Error] 'pyttsx3' is not installed. Please run: pip install pyttsx3")
                print(f"AI Console fallback: \"{text}\"")
                return
            except Exception as e:
                print(f"\n[TTS Error] Failed to initialize pyttsx3 engine: {e}")
                print(f"AI Console fallback: \"{text}\"")
                return

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"\n[TTS Error] Playback failed: {e}")
            print(f"AI Console fallback: \"{text}\"")
