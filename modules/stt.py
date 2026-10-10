from faster_whisper import WhisperModel

model = None


def voice_to_text(path):
    """Audio ko wapas text banao. Return: (text, language)."""
    global model
    if model is None:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")

    segments, info = model.transcribe(path)

    text = ""
    for seg in segments:
        text += seg.text

    return text.strip(), info.language
