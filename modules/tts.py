import os
from datetime import datetime

from gtts import gTTS

audio_dir = "audio_files"


def text_to_voice(text, lang="en"):
    """Text ko mp3 me save karo aur path return karo."""
    os.makedirs(audio_dir, exist_ok=True)

    # Har run ki alag file, warna purani audio overwrite ho jati thi
    name = datetime.now().strftime("voice_%Y%m%d_%H%M%S.mp3")
    path = os.path.join(audio_dir, name)

    try:
        gTTS(text=text, lang=lang).save(path)
    except Exception:
        # gTTS fail hone par 0 byte ki khaali mp3 chhod deta hai,
        # aur agli baar Whisper usi toote file ko padhne lagta hai
        if os.path.exists(path) and os.path.getsize(path) == 0:
            os.remove(path)
        raise

    return path