class SpeechToText:
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the audio file at audio_path.
        Returns:
            The transcribed text as a string.
        """
        raise NotImplementedError("STT implementations must implement transcribe")
