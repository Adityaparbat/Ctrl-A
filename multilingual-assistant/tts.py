from gtts import gTTS
import playsound
from config import TTS_LANGUAGE


def speak(text: str) -> None:
    """Convert text to speech and play it using system audio."""
    try:
        tts = gTTS(text=text, lang=TTS_LANGUAGE)
        tts.save("reply.mp3")
        playsound.playsound("reply.mp3")
    except Exception as e:
        print("⚠️ TTS Error:", e)
