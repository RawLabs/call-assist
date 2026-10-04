import math
import struct
from audio.base import VoiceActivityDetector

class RMSVoiceActivityDetector(VoiceActivityDetector):
    def __init__(self, threshold: float = 300.0):
        """
        threshold: RMS amplitude value above which sound is classified as speech.
                   300.0 is a reasonable default for standard headsets/mics.
        """
        self.threshold = threshold

    def is_speech(self, audio_chunk: bytes, sample_rate: int = 16000) -> bool:
        # Assuming 16-bit PCM Mono (2 bytes per sample)
        count = len(audio_chunk) // 2
        if count == 0:
            return False
        
        try:
            # Unpack signed short integers
            samples = struct.unpack(f"{count}h", audio_chunk)
        except Exception:
            # Fallback if chunk size is mismatched
            return False
        
        # Calculate RMS (Root Mean Square)
        sum_squares = sum(float(s) ** 2 for s in samples)
        rms = math.sqrt(sum_squares / count)
        
        return rms > self.threshold
