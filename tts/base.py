class TextToSpeech:
    def speak(self, text: str) -> None:
        """
        Synthesizes the given text and plays it back through the local speakers.
        Blocks until playback is complete (unless interrupted).
        """
        raise NotImplementedError("TTS implementations must implement speak")
