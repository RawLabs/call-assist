# Lazy-import sounddevice and soundfile to prevent crashes on startup if dependencies are missing
sd = None
sf = None

def play_wav(file_path: str) -> None:
    """Reads a WAV file and plays it back through the default system speakers."""
    global sd, sf
    if sd is None:
        import sounddevice as sd
    if sf is None:
        import soundfile as sf
        
    try:
        data, fs = sf.read(file_path)
        sd.play(data, fs)
        sd.wait()  # Blocks until audio is finished playing
    except Exception as e:
        print(f"\n[Playback Error] {e}. Cannot play audio file: {file_path}")

def stop_playback() -> None:
    """Stops all active audio playback immediately. Used for barge-in."""
    global sd
    if sd is None:
        import sounddevice as sd
    try:
        sd.stop()
    except Exception:
        pass
