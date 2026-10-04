import os
import wave
import tempfile
import time
import numpy as np
from audio.base import VoiceActivityDetector

# Lazy-import sounddevice to prevent crashes on startup if libportaudio is missing
sd = None

class AudioRecorder:
    def __init__(self, vad: VoiceActivityDetector, sample_rate: int = 16000, chunk_size: int = 1024):
        self.vad = vad
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._temp_files = []

    def record_until_silence(self, max_silence_seconds: float = 1.5, timeout_seconds: float = 6.0) -> str:
        """
        Listens to the microphone.
        If speech is detected, it records until silence is detected.
        If no speech is detected within timeout_seconds, returns None (representing silence).
        
        Returns:
            Path to the recorded WAV file, or None if timeout / silence occurred.
        """
        global sd
        if sd is None:
            import sounddevice as sd

        recorded_frames = []
        speech_started = False
        silence_start_time = None
        start_time = time.time()

        # Open the microphone stream (16-bit mono PCM)
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
                while True:
                    # Read a chunk from the microphone
                    data, overflowed = stream.read(self.chunk_size)
                    chunk_bytes = data.tobytes()

                    # Check for active speech in the chunk
                    is_active = self.vad.is_speech(chunk_bytes, self.sample_rate)

                    current_time = time.time()

                    if not speech_started:
                        # Waiting for speech to start
                        if is_active:
                            speech_started = True
                            recorded_frames.append(data)
                        elif (current_time - start_time) > timeout_seconds:
                            # Timeout: caller remained silent
                            return None
                    else:
                        # Recording active speech
                        recorded_frames.append(data)
                        if not is_active:
                            if silence_start_time is None:
                                silence_start_time = current_time
                            elif (current_time - silence_start_time) > max_silence_seconds:
                                # Silence threshold reached, stop recording
                                break
                        else:
                            # Reset silence timer when speech is heard
                            silence_start_time = None

        except Exception as e:
            # Handle situations where microphone is unavailable or error occurs
            print(f"\n[Microphone Error] {e}. Falling back to manual text input.")
            return None

        if not recorded_frames:
            return None

        # Concatenate and save to WAV
        audio_data = np.concatenate(recorded_frames, axis=0)
        
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        self._temp_files.append(temp_wav.name)
        
        with wave.open(temp_wav.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes = 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())

        return temp_wav.name

    def cleanup(self):
        """Cleans up temporary WAV files generated during the session."""
        for path in self._temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
        self._temp_files.clear()
