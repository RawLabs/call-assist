class VoiceActivityDetector:
    def is_speech(self, audio_chunk: bytes, sample_rate: int = 16000) -> bool:
        """
        Determines whether the given raw audio chunk contains active speech.
        
        Args:
            audio_chunk: Raw PCM audio bytes (16-bit Mono).
            sample_rate: The audio sample rate (typically 16000 Hz).
        Returns:
            True if speech is detected, False otherwise.
        """
        raise NotImplementedError("VAD implementations must implement is_speech")
