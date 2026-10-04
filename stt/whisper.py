from stt.base import SpeechToText

class WhisperSTT(SpeechToText):
    def __init__(self, model_size: str = "tiny"):
        self.model_size = model_size
        self.model = None

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the given audio file locally using faster-whisper.
        Downloads the tiny model on first run if not already present.
        """
        if not audio_path:
            return ""

        # Lazy loading the model so application startup remains fast
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                # Runs on CPU by default with 8-bit integer quantization for speed/ram optimization
                self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            except ImportError:
                print("\n[STT Error] 'faster-whisper' package is not installed. Please run: pip install faster-whisper")
                return "[Error: faster-whisper missing]"
            except Exception as e:
                print(f"\n[STT Error] Failed to load Whisper model: {e}")
                return "[Error: Whisper load failed]"

        try:
            segments, info = self.model.transcribe(audio_path, beam_size=5)
            text = " ".join(segment.text for segment in segments)
            return text.strip()
        except Exception as e:
            print(f"\n[STT Error] Transcription failed: {e}")
            return "[Error: Transcription failed]"
