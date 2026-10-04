from stt.base import SpeechToText

class MockSTT(SpeechToText):
    def __init__(self, predefined_inputs: list = None):
        self.predefined_inputs = predefined_inputs or []
        self.input_index = 0

    def transcribe(self, audio_path: str = None) -> str:
        """
        Transcribes by using predefined inputs first (useful for testing),
        then falling back to interactive terminal input.
        """
        if self.input_index < len(self.predefined_inputs):
            text = self.predefined_inputs[self.input_index]
            self.input_index += 1
            return text
        
        try:
            # Simple prompt for manual simulation mode
            val = input("\nCaller: ")
            return val.strip()
        except (KeyboardInterrupt, EOFError):
            # Safe escape word
            return "operator"
